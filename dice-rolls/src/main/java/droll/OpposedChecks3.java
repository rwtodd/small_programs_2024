package droll;

import java.util.Random;

/**
 * <p>This class calculates the odds of winning an opposed
 * ability-score check.  The idea is:</p>
 * <ol>
 *     <li>Each side tries to roll under their ability score</li>
 *     <li>If it's harder/easier for one side, a bonus or penalty can be applied to the score first.</li>
 *     <li>If one side's score is 2 better than the other, they get to take the best of 2 rolls.</li>
 *     <li>If one side's score is 4 better than the other, they get to take the best of 3 rolls.</li>
 * </ol>
 * <p>It should add color to the check if both fail, or if there are one or more
 * ties.  But, do the percentages work out ok?  This class is to investigate that.</p>
 */
public class OpposedChecks3 {
    private static final Random rng = new Random();

    /**
     * Run one opposed check between scoreA and scoreB.
     * @param scoreA the effective ability score of participant A
     * @param scoreB the effective ability score of participant B
     * @return the result of the opposed check, from scoreA's perspective.
     */
    public static CheckResult run(int scoreA, int scoreB) {
        int rollA = rng.nextInt(1,21);
        int rollB = rng.nextInt(1,21);

        if((scoreB - scoreA) >= 2) {
            rollB = Math.min(rollB, rng.nextInt(1,21));
        } else if((scoreA - scoreB) >= 3) {
            rollA = Math.min(rollA, rng.nextInt(1,21));
        }

        // roll a third die if the difference is greater than 6...
        if((scoreB - scoreA) >= 4) {
            rollB = Math.min(rollB, rng.nextInt(1,21));
        } else if((scoreA - scoreB) >= 6) {
            rollA = Math.min(rollA, rng.nextInt(1,21));
        }

        int diff = (scoreA - rollA) - (scoreB - rollB);
        return CheckResult.of(diff);
    }

    public static void allProbs(int scoreA, int scoreB) {
        int fb5 = 0;
        int f = 0;
        int t = 0;
        int p = 0;
        int pb5 = 0;
        for(int trial = 0; trial < 50000; ++trial) {
            final CheckResult r = run(scoreA, scoreB);
            switch(r) {
                    case FailBy5 -> ++fb5;
                    case Fail -> ++f;
                    case Tie -> ++t;
                    case Pass -> ++p;
                    case PassBy5 -> ++pb5;
            }
            }
        System.out.printf("Fail %.1f (Fb5 %.1f F %.1f) / T %.1f / Pass %.1f (P %.1f Pb5 %.1f)\n",
                (fb5+f)/500.0, fb5/500.0, f/500.0, t/500.0, (pb5+p)/500.0, p/500.0, pb5/500.0);
    }

}
