package droll;

/**
 * An enumeration to describe the result of an ability score or NWP check.
 */
public enum CheckResult {
    FailBy5, Fail, Tie, Pass, PassBy5;

    /**
     * Convert a numeric score into a CheckResult
     * @param value The score.
     * @return the equivalent CheckResult.
     */
    public static CheckResult of(int value) {
        if(value <= -5) return CheckResult.FailBy5;
        else if(value < 0) return CheckResult.Fail;
        else if(value == 0) return CheckResult.Tie;
        else if(value >= 5) return CheckResult.PassBy5;
        else return CheckResult.Pass;
    }

    /**
     * Is this an extreme result (by 5 or more!)
     * @return true if the result is FailBy5 or PassBy5.
     */
    public boolean byFive() {
        return this.equals(FailBy5) || this.equals(PassBy5);
    }

    /**
     * just tell me if the result is a kind of pass...
     */
    public boolean isAPass() { return this == Pass || this == PassBy5; }
}
