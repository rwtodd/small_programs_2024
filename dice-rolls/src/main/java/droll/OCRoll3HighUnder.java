package droll;

/**
 * Similar to OCRollHighUnder, except we always do three rolls, and
 * a roll that matches the ability score counts as double.  Ties go
 * to the higher of the scores.
 */
 public class OCRoll3HighUnder extends OpposedCheck {

     private int scoreOneRoll(final int roll, final int score) {
         return switch(Integer.signum(score - roll)) {
             case -1 -> 0;
             case 0 -> 2;
             default -> 1;
         };
     }

     private int scoreOneContest(final int rollA, final int rollB, final int scoreA, final int scoreB) {
        int resultA = scoreOneRoll(rollA, scoreA);
        int resultB = scoreOneRoll(rollB, scoreB);
        return switch(Integer.signum(resultA - resultB)) {
            case 1 -> 1;
            case 0 -> (rollA == rollB) ? Integer.signum(scoreA - scoreB) : Integer.signum(rollA - rollB);
            default -> -1;
        };
     }

     @Override
     public CheckResult runOne(final int scoreA, final int scoreB) {
         final int total = scoreOneContest(dice.roll(), dice.roll(), scoreA, scoreB) +
                 scoreOneContest(dice.roll(), dice.roll(), scoreA, scoreB) +
                 scoreOneContest(dice.roll(), dice.roll(), scoreA, scoreB);

         return switch(total) {
             case -3 -> CheckResult.FailBy5;
             case -2, -1 -> CheckResult.Fail;
             case 0 -> CheckResult.Tie;
             case 1, 2 -> CheckResult.Pass;
             case 3 -> CheckResult.PassBy5;
             default -> throw new IllegalStateException("Out of bound total!");
         };
    }

    @Override
    public void printDescription() {
        System.out.println("Try to roll all three high but under your score. Rolling your exact score is best!");
    }

    public OCRoll3HighUnder(Dice dice) {
        super("Roll High Three Times (but Under Score)", dice);
    }

}
