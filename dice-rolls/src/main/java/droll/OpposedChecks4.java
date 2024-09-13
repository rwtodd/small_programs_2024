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
        Dice.runTrials(50_000, scoreA, scoreB, OpposedChecks4::run);
    }
}
