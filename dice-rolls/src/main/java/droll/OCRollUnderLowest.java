package droll;

import java.util.Random;

/**
 * <p>This class calculates the odds of winning an opposed
 * ability-score check.  The idea is:</p>
 * <ol>
 *     <li>Each side tries to roll under their ability score</li>
 *     <li>If it's harder/easier for one side, a bonus or penalty can be applied to the score first.</li>
 *     <li>The one who rolls under by the most (or over by the least), wins.</li>
 *     <li>If they tie, you would roll again.</li>
 * </ol>
 * <p>It should add color to the check if both fail, or if there are one or more
 * ties.  But, do the percentages work out ok?  This class is to investigate that.</p>
 */
public class OCRollUnderLowest extends OpposedCheck {

    @Override public CheckResult runOne(int scoreA, int scoreB) {
        int rollA = dice.roll();
        int rollB = dice.roll();
        int diff = (scoreA - rollA) - (scoreB - rollB);
        return CheckResult.of(diff);
    }

    public OCRollUnderLowest(Dice dice) {
        super("Roll-Under Lowest", dice);
    }

    @Override public void printDescription() {
        System.out.println("Roll against score.  The one who gets farthest below (or least above)");
        System.out.println("their score wins.");
    }
}
