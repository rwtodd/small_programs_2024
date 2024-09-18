package droll;

public abstract class OpposedCheck {

    protected final String name;
    protected final Dice dice;

    @Override public String toString() {
        return String.format("%s (%s)", name, dice);
    }

    public OpposedCheck(String name, Dice dice) {
        this.name = name;
        this.dice = dice;
    }

    /**
     * Run one opposed check between scoreA and scoreB.
     *
     * @param scoreA the effective ability score of participant A
     * @param scoreB the effective ability score of participant B
     * @return the result of the opposed check, from participant A's perspective.
     */
    public abstract CheckResult runOne(final int scoreA, final int scoreB);

    /**
     * Print a description of the opposed check mechanic.
     */
    public abstract void printDescription();

    public void runMany(final int count, final int scoreA, final int scoreB) {
        int fb5 = 0;
        int f = 0;
        int t = 0;
        int p = 0;
        int pb5 = 0;
        for(int trial = 0; trial < count; ++trial) {
            final CheckResult r = runOne(scoreA, scoreB);
            switch(r) {
                case FailBy5 -> ++fb5;
                case Fail -> ++f;
                case Tie -> ++t;
                case Pass -> ++p;
                case PassBy5 -> ++pb5;
            }
        }
        final double divisor = count / 100.0;
        System.out.printf("[%s]: Fail %.1f (Fb5 %.1f F %.1f) / T %.1f / Pass %.1f (P %.1f Pb5 %.1f)\n",
                this, (fb5+f)/divisor, fb5/divisor, f/divisor, t/divisor, (pb5+p)/divisor, p/divisor, pb5/divisor);
    }

    public void runMany2OutOf3(final int count, final int scoreA, final int scoreB) {
        int winCount = 0;
        for(int trial = 0; trial < count; ++trial) {
            int winsA = 0;
            int winsB = 0;
            while( (winsA == winsB) || (Math.max(winsA,winsB) < 3) ) {
                switch(runOne(scoreA, scoreB)) {
                    case Tie -> { ++winsA; ++winsB; }
                    case Pass,PassBy5 -> winsA += 2;
                    case Fail,FailBy5 -> winsB += 2;
                }
            }
            if(winsA > winsB) ++winCount;
        }
        System.out.printf("[%s]: A wins %.1f%% of 2-of-3 contests!\n", this, 100.0 * winCount / count);
    }

}
