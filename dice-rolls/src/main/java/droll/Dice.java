package droll;

import java.util.Random;
import java.util.function.BiFunction;

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

    private static final Random rng = new Random();

    public static int middleNumber(int a, int b, int c) {
        return Math.max(
                Math.min(a,b),
                Math.min( Math.max(a,b), c)
        );
    }

    public static int d20() { return rng.nextInt(1,21); }

    public static int middleOf3d20() {
        return middleNumber(rng.nextInt(1,21), rng.nextInt(1,21), rng.nextInt(1,21));
    }

    public static void runTrials(final int count, final int scoreA, final int scoreB, final BiFunction<Integer,Integer,CheckResult> oneTrial) {
        int fb5 = 0;
        int f = 0;
        int t = 0;
        int p = 0;
        int pb5 = 0;
        for(int trial = 0; trial < count; ++trial) {
            final CheckResult r = oneTrial.apply(scoreA, scoreB);
            switch(r) {
                case FailBy5 -> ++fb5;
                case Fail -> ++f;
                case Tie -> ++t;
                case Pass -> ++p;
                case PassBy5 -> ++pb5;
            }
        }
        final double divisor = count / 100.0;
        System.out.printf("Fail %.1f (Fb5 %.1f F %.1f) / T %.1f / Pass %.1f (P %.1f Pb5 %.1f)\n",
                (fb5+f)/divisor, fb5/divisor, f/divisor, t/divisor, (pb5+p)/divisor, p/divisor, pb5/divisor);
    }

    public static void trialsOf2OutOf3(final int count, final int scoreA, final int scoreB, final BiFunction<Integer,Integer,CheckResult> oneTrial) {
        int winCount = 0;
        for(int trial = 0; trial < count; ++trial) {
            int winsA = 0;
            int winsB = 0;
            while( (winsA == winsB) || (Math.max(winsA,winsB) < 3) ) {
                switch(oneTrial.apply(scoreA, scoreB)) {
                    case Tie -> { ++winsA; ++winsB; }
                    case Pass,PassBy5 -> winsA += 2;
                    case Fail,FailBy5 -> winsB += 2;
                }
            }
            if(winsA > winsB) ++winCount;
        }
        System.out.printf("A wins %.1f%% of 2-of-3 contests!\n", 100.0 * winCount / count);
    }
}
