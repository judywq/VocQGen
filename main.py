import pandas as pd
from lib.chat import MyBotWrapper
from lib.parser import SentGenParser, DerivativeParser, RationalParser
from lib.utils import fill_cloze, get_date_str, read_from_cache, write_to_cache, setup_log, setup_randomness
from lib.io import read_data, write_data
from lib.word_cluster import WordCluster, WordFamily
from lib.nlp_helper import pos_check
import setting

import logging
logger = logging.getLogger(__name__)


def main():
    now = get_date_str()
    path = 'data/input/AWL.xlsx'
    sublist = setting.SUBLIST
    fn_data = f'./data/output/{now}-AWL-sublist-{sublist}-cloze.xlsx'
    fn_log = f'./log/excel/{now}-log.xlsx'
    fn_inflections = f'./log/excel/{now}-inflections.xlsx'
    inflection_columns = ['word', 'tag', 'lemm', 'unimorph', 'final']

    logger.info(f"Try loading from cache...")
    word_cluster = read_from_cache(path, sublist)
    if not word_cluster:
        logger.info(f"WordCluster cache not found, load...")
        word_cluster = load_sublist(path, sublist=sublist)
        write_to_cache(path, sublist, word_cluster)
        logger.info(f"WordCluster written to cache")
    else:
        logger.info(f"WordCluster loaded from cache: {path}")
    df_inflections = pd.DataFrame(word_cluster.inflection_log, columns=inflection_columns)
    write_data(df_inflections, fn_inflections)
    logger.info(f"Inflections saved to {fn_inflections}")
    
    word_families = select_word_families(word_cluster, start=setting.KEYWORD_START_POS, max_count=setting.KEYWORD_COUNT)
    n_total = len(word_families)
    logger.info(f"Start generating cloze sentences for {n_total} words...")

    bot_sent_gen = MyBotWrapper(parser=SentGenParser(), temperature=0.9)
    # bot_derive = MyBotWrapper(parser=DerivativeParser(), temperature=0.1)
    bot_rational = MyBotWrapper(parser=RationalParser(), temperature=0)

    log_columns = ['Date', 'Task', 'Keyword', 'Tag', 'Prompt', 'Raw Response', 'Parsed Result', 'Success']
    log_data = []
    
    columns = ['Sentence', 'Correct Answer', *[f'Distractor {i}' for i in range(1, setting.DISTRACTOR_COUNT+1)]]
    data = []
    for i, word_family in enumerate(word_families):
        for word in word_family.get_shuffled_words():
            # FIXME: word is '' if inflections not generated correctly
            if not word:
                logger.warning(f"Empty word in word family: {repr(word_family)}")
                continue
            
            keyword = word.surface
            keyword_tag = word.tag
            
            clozed_sentence = None
            for trial in range(setting.RETRY_COUNT_FOR_SINGLE_WORD):
                # print(f"{repr(w)}: {candidates}")
                r = bot_sent_gen.run(inputs={"word": keyword, "tag": keyword_tag, "domain": setting.DOMAIN, "level_start": setting.LEVEL_START, "level_end": setting.LEVEL_END})
                suc = r.get('success')
                log_data.append([get_date_str(), bot_sent_gen.task_name, keyword, keyword_tag, r.get('prompt'), r.get('raw_response'), r.get('result'), suc])
                
                if suc:
                    clozed_sentence = r.get('result')
                    sentence = fill_cloze(clozed_sentence, keyword)

                    suc = pos_check(inputs={"word": keyword, "tag": keyword_tag, "sentence": sentence})
                    log_data.append([get_date_str(), "POS Check", keyword, keyword_tag, f"Tag: {keyword_tag}, Sentence: {sentence}", "-", "-", suc])
                
                if suc:
                    break
                
            if not suc:
                logger.error(f"Failed to generate sentence for '{repr(word)}'")
            else:
                # Successfully generated a sentence, now generate distractors
                distractors = fill_distractors(bot_rational, word_cluster, word, clozed_sentence,n_distractors=setting.TEST_DISTRACTOR_COUNT, log_data=log_data)
                
                if len(distractors) < setting.DISTRACTOR_COUNT:
                    logger.error(f"Failed to generate enough distractors for '{word}'")
                else:
                    data.append([clozed_sentence, keyword, *distractors])
                    msg = "\n".join([f"{i+1}/{n_total}: " + "-" * 80,
                            f"Sentence: {clozed_sentence}",
                            f"Keyword: {keyword}",
                            "Distractors: " + ", ".join(distractors),])
                    logger.info(msg)
                    df = pd.DataFrame(data, columns=columns)
                    write_data(df, fn_data)
                    # Successfully generated a cloze sentence, break the word loop, goto next word family
                    break

            df_log = pd.DataFrame(log_data, columns=log_columns)
            write_data(df_log, fn_log)
            # End of word loop
        # End of word family loop
    
    logger.info(f"Done. Data saved to {fn_data}")


def fill_distractors(bot_rational, word_cluster, word, sentence, n_distractors, log_data=[], max_trials=5):
    excepts = [word]
    distractors = []
    for i in range(max_trials):
        candidates = word_cluster.find_distractors(word.tag, excepts=excepts, n=n_distractors)
        excepts += candidates
        
        if len(candidates) == 0:
            logger.warning(f"No more distractor candidates for '{word}'")
            break
        
        r = bot_rational.run(inputs={"keyword": word, "candidates": candidates, "sentence": sentence})
        suc = r.get('success')
        good_candidates = r.get('good_candidates')
        log_data.append([get_date_str(), bot_rational.task_name, word.surface, word.tag, r.get('prompt'), r.get('raw_response'), good_candidates, suc])
        if not suc:
            logger.error(f"Failed to decide proper distractors for {word}")
            continue
        # Make sure the distractors do not exceed the max count
        distractors += [str(w) for w in good_candidates]
        
        if len(distractors) == setting.DISTRACTOR_COUNT:
            break
        elif len(distractors) > setting.DISTRACTOR_COUNT:
            distractors = distractors[:setting.DISTRACTOR_COUNT]
            break
        else:
            logger.debug(f"Trial {i}: {len(distractors)} distractors collected in total.")
    return distractors


def load_sublist(path, sublist=1, max_count=-1):
    """Load a sublist from a file as a WordCluster object
    """
    df = read_data(path=path)
    df = df[df['Sublist'] == sublist]
    df = df.astype({'Headword': 'str', 'Related word forms': 'str'})
    wc = WordCluster()
    for i, row in df.iterrows():
        headword = row['Headword']
        logger.info(f"Processing word family for '{headword}'")
        # related_words = row['Related word forms'].split(',')
        # Do not derive for now
        related_words = []
        wc.add_item(headword, related_words)
        if max_count > 0 and i >= max_count:
            break
    logger.debug("Shape of data: {}\n{}".format(df.shape, df.head()))
    # wc.print()
    return wc


def select_word_families(word_cluster: WordCluster, start=0, max_count=-1) -> list[WordFamily]:
    word_families = []
    for wf in word_cluster.word_family_list[start:]:
        word_families.append(wf)
        if max_count > 0 and len(word_families) >= max_count:
            break
    return word_families
################################

    
if __name__ == '__main__':
    setup_randomness()
    setup_log()
    main()
