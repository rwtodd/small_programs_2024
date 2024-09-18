package droll;

public class D20 extends Dice {
    @Override public int roll() { return rng.nextInt(1,21); }

    public D20() { super("1d20"); }
}
