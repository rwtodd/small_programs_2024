package droll;

import java.util.Random;
import java.util.function.BiFunction;

public abstract class Dice {

    /**
     * Calculate the middle of three numbers.
     * @param a a number
     * @param b a second number
     * @param c a third number
     * @return the middle of the numbers
     */
    public static int middleNumber(int a, int b, int c) {
        return Math.max(
                Math.min(a,b),
                Math.min( Math.max(a,b), c)
        );
    }

    protected final Random rng = new Random();
    protected final String description;

    public Dice(String description) {
        this.description = description;
    }

    public abstract int roll();

    @Override public String toString() {
        return description;
    }
}
