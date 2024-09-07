package droll;

public abstract class Dice {
    private static final double[] AT_LEAST_3d6 = new double[] {
        100.00, 99.54, 98.15, 95.37, 90.74, 83.80, 74.07, 62.50, 50.00, 37.50, 25.93, 16.20, 9.26, 4.63, 1.85, 0.46
    };

    /**
     * Calculates the probability that you roll at least `n` on 3d6.
     * @param n the target to-roll number
     * @return the percentage chance (0 to 100)
     */
    public static double atLeastOn3d6(int n) {
        if((n < 3) || (n > 18)) return 0.0;
        return AT_LEAST_3d6[n-3];
    }
}
