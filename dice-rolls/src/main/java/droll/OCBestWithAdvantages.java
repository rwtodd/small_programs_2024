package droll;

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
public class OCBestWithAdvantages extends OpposedCheck {

    @Override
    public CheckResult runOne(final int scoreA, final int scoreB) {
        int rollA = dice.roll();
        int rollB = dice.roll();

        if((scoreB - scoreA) >= 2) {
            rollB = Math.min(rollB, dice.roll());
        } else if((scoreA - scoreB) >= 3) {
            rollA = Math.min(rollA, dice.roll());
        }

        // roll a third die if the difference is greater than 6...
        if((scoreB - scoreA) >= 4) {
            rollB = Math.min(rollB, dice.roll());
        } else if((scoreA - scoreB) >= 6) {
            rollA = Math.min(rollA, dice.roll());
        }

        int diff = (scoreA - rollA) - (scoreB - rollB);
        return CheckResult.of(diff);
    }

    public OCBestWithAdvantages(Dice dice) {
        super("Roll w/Advantages", dice);
    }

    @Override public void printDescription() {
        System.out.println("An opposed check where whover has the better ability score");
        System.out.println("gets to keep the best of multiple rolls.");
    }
}
