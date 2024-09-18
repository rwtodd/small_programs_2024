package droll;

/**
 * Simulate checks like I saw in Psionic 2e Handbook:
 * Roll and try to get as high as possible while staying under the
 * score.
 */
 public class OCRollHighUnder extends OpposedCheck {

    /**
     * Method to break ties in the rolls.
     */
    public enum TieBreaker { HIGHEST_SCORE, TIE; };

    protected final TieBreaker tieBreaker;

    @Override
    public CheckResult runOne(final int scoreA, final int scoreB) {
        final int rollA = dice.roll();
        final int rollB = dice.roll();
        CheckResult result = CheckResult.Tie;

        if(rollA <= scoreA) {
            if(rollB <= scoreB) {
                // both pass, return whoever is greater...
                result = switch(Integer.signum(rollA-rollB)) {
                   case -1 -> CheckResult.Fail;
                   case 1 -> CheckResult.Pass;
                   default -> CheckResult.Tie;
                };
            } else {
                // B failed... so A wins
                result = CheckResult.Pass;
            }
        } else {
            // rollA failed, so... it's either a tie or a fail...
            result = (rollB <= scoreB) ? CheckResult.Fail : CheckResult.Tie;
        }

        if(result == CheckResult.Tie && tieBreaker == TieBreaker.HIGHEST_SCORE) {
            result = switch(Integer.signum(scoreA - scoreB)) {
                case -1 -> CheckResult.Fail;
                case 1 -> CheckResult.Pass;
                default -> CheckResult.Tie;
            };
        }
        return result;
    }

    @Override
    public void printDescription() {
        System.out.println("Try to roll high but under your score.");
    }

    public OCRollHighUnder(TieBreaker tb, Dice dice) {
        super("Roll High but Under", dice);
        tieBreaker = tb;
    }

}
