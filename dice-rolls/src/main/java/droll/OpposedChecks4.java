package droll;

/**
 * Run a type-1 check, but as a contest where the victor has to win 2 out of 3.
 */
public class OpposedChecks4 {

    /**
     * Run one opposed check between scoreA and scoreB.
     *
     * @param scoreA the effective ability score of participant A
     * @param scoreB the effective ability score of participant B
     * @return the result of the opposed check, from scoreA's perspective.
     */
    public static CheckResult run(int scoreA, int scoreB) {
        int winsA = 0;
        int winsB = 0;
        while (Math.max(winsA,winsB) < 2 || (winsA == winsB)) {
            final var cr = OpposedChecks1.run(scoreA, scoreB);
            switch(cr) {
                case Pass, PassBy5 -> ++winsA;
                case Fail, FailBy5 -> ++winsB;
                case Tie -> { ++winsA; ++winsB; }
            }
        }
        return (winsA > winsB) ? CheckResult.Pass : CheckResult.Fail;
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
