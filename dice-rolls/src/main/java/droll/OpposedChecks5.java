package droll;

/**
 * Simulate checks like I saw in Psionic 2e Handbook:
 * Roll d20, and try to get as high as possible while staying under the
 * score.
 */
abstract public class OpposedChecks5 {

    /**
     * Run one opposed check between scoreA and scoreB.
     *
     * @param scoreA the effective ability score of participant A
     * @param scoreB the effective ability score of participant B
     * @return the result of the opposed check, from scoreA's perspective.
     */
    public static CheckResult run(final int scoreA, final int scoreB) {
        final int rollA = Dice.middleOf3d20();
        final int rollB = Dice.middleOf3d20();

        if(rollA <= scoreA) {
            if(rollB <= scoreB) {
                // both pass, return whoever is greater...
                return switch(Integer.signum(rollA-rollB)) {
                   case -1 -> CheckResult.Fail;
                   case 1 -> CheckResult.Pass;
                   default -> CheckResult.Tie;
                };
            } else {
                // B failed... so A wins
                return CheckResult.Pass;
            }
        } else {
            // rollA failed, so... it's either a tie or a fail...
            if(rollB <= scoreB) return CheckResult.Fail;
            else return CheckResult.Tie;
        }
    }

    public static void allProbs(int scoreA, int scoreB) {
        Dice.runTrials(50_000, scoreA, scoreB, OpposedChecks5::run);
    }

    public static void twoOfThree(int scoreA, int scoreB) {
        Dice.trialsOf2OutOf3(50_000, scoreA, scoreB, OpposedChecks5::run);
    }

}
