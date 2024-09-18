package droll;

import java.util.Random;

/**
 * <p>This class calculates the odds of winning an opposed
 * ability-score check.  The idea is:</p>
 * <ol>
 *     <li>Each side rolls adds their ability score to the roll.</li>
 *     <li>If it's harder/easier for one side, a bonus or penalty can be applied to the score first.</li>
 *     <li>The highest score wins.</li>
 *     <li>If they tie, you would roll again.</li>
 * </ol>
 */
public class OCAddRollToScore extends OpposedCheck {

    @Override public CheckResult runOne(int scoreA, int scoreB) {
        final int rollA = dice.roll();
        final int rollB = dice.roll();
        return CheckResult.of((scoreA + rollA) - (scoreB + rollB));
    }

    public OCAddRollToScore(Dice dice) {
        super("Roll plus score", dice);
    }

    @Override public void printDescription() {
        System.out.println("Roll and add the value to your score.  The highest score wins!");
    }

}