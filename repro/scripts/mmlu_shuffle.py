# Fixed random order of the full MMLU test set (seed 0), so a partial run is a uniform random subset and a full run is unchanged.
# Usage: mmlu_shuffle.py data/mmlu_test.jsonl data/mmlu_test_shuf.jsonl
import sys, random
L = open(sys.argv[1]).read().splitlines(); random.Random(0).shuffle(L); open(sys.argv[2], 'w').write("\n".join(L) + "\n")
