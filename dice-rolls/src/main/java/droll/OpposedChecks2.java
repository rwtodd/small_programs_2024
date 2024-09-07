package droll;

import java.util.Random;

/**
 * <p>This class calculates the odds of winning an opposed
 * ability-score check.  The idea is:</p>
 * <ol>
 *     <li>Each side rolls 3d20 and adds their ability score to the middle value.</li>
 *     <li>If it's harder/easier for one side, a bonus or penalty can be applied to the score first.</li>
 *     <li>The highest score wins.</li>
 *     <li>If they tie, you would roll again.</li>
 * </ol>
 * <p>It should add color to the check if both fail, or if there are one or more
 * ties.  But, do the percentages work out ok?  This class is to investigate that.</p>
 */
public class OpposedChecks2 {
    private static final Random rng = new Random();

    private static int middleNumber(int a, int b, int c) {
        return Math.max(
                Math.min(a,b),
                Math.min( Math.max(a,b), c)
        );
    }

    /**
     * Run one opposed check between scoreA and scoreB.
     *
     * @param scoreA the effective ability score of participant A
     * @param scoreB the effective ability score of participant B
     * @return the result of the opposed check, from scoreA's perspective.
     */
    public static CheckResult run(int scoreA, int scoreB) {
        int rollA = middleNumber(rng.nextInt(1, 21), rng.nextInt(1, 21), rng.nextInt(1, 21));
        int rollB = middleNumber(rng.nextInt(1, 21), rng.nextInt(1, 21), rng.nextInt(1, 21));
        int diff = (scoreA - rollA) - (scoreB - rollB);
        int diff2 = (scoreA + rollA) - (scoreB + rollB);
        System.err.printf("rollA %d and rollB %d\n", rollA, rollB);
        System.err.printf("diff1 %d and diff2 %d\n", diff, diff2);
        return CheckResult.of(diff2);
    }

    public static void allProbs(int scoreA, int scoreB) {
        int fb5 = 0;
        int f = 0;
        int t = 0;
        int p = 0;
        int pb5 = 0;
        for (int rollA1 = 1; rollA1 <= 20; ++rollA1) {
            for (int rollA2 = 1; rollA2 <= 20; ++rollA2) {
                for (int rollA3 = 1; rollA3 <= 20; ++rollA3) {
                    int rollA = middleNumber(rollA1, rollA2, rollA3);
                    for (int rollB1 = 1; rollB1 <= 20; ++rollB1) {
                        for (int rollB2 = 1; rollB2 <= 20; ++rollB2) {
                            for (int rollB3 = 1; rollB3 <= 20; ++rollB3) {
                                int rollB = middleNumber(rollB1, rollB2, rollB3);
                                int diff = (scoreA + rollA) - (scoreB + rollB);
                                switch (CheckResult.of(diff)) {
                                    case FailBy5 -> ++fb5;
                                    case Fail -> ++f;
                                    case Tie -> ++t;
                                    case Pass -> ++p;
                                    case PassBy5 -> ++pb5;
                                }
                            }
                        }
                    }
                }
            }
        }

        System.out.printf("!Fail %.1f (Fb5 %.1f F %.1f) / T %.1f / Pass %.1f (P %.1f Pb5 %.1f)\n",
                (fb5 + f) / 640_000.0, fb5 / 640_000.0, f / 640_000.0, t / 640_000.0, (pb5 + p) / 640_000.0, p / 640_000.0, pb5 / 640_000.0);
    }
}