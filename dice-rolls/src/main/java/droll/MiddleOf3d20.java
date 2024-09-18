package droll;

public class MiddleOf3d20 extends Dice {
    @Override public int roll() {
        return Dice.middleNumber(rng.nextInt(1,21), rng.nextInt(1,21), rng.nextInt(1,21));
    }

    public MiddleOf3d20() { super("Middle of 3d20"); }
}
