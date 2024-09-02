import java.util.BitSet;

class Square {
    private final int dimension;
    private final int[] values;

    Square() {
        dimension = 1;
        values = new int[] { 1 };
    }

    private static final int[] OFFSET_X = new int[] { 1, 2, 0, 0, 1, 2, 2, 0, 1 };
    private static final int[] OFFSET_Y = new int[] { 2, 0, 1, 0, 1, 2, 1, 2, 0 };

    Square(Square base) {
        final int bdim = base.getDimension();
        dimension = bdim * 3;
        values = new int[dimension*dimension];

        // ok, now fill the array by looping over the base...
        for(int by = 0; by < base.getDimension(); ++by) {
            for(int bx = 0; bx < base.getDimension(); ++bx) {
                // locate this 9x9 portion of the new square
                final int sqX = bx * 3;
                final int sqY = by * 3;

                int value = base.get(bx,by);
                for(int idx = 0; idx < OFFSET_X.length; ++idx) {
                    values[(sqY+OFFSET_Y[idx])*dimension+sqX+OFFSET_X[idx]] = value;
                    value += bdim*bdim;
                }
            }
        }
    }

    int getDimension() { return dimension; }

    private int get(int x, int y) {
        return values[y*dimension + x];
    }

    int getSum() {
        int tally = 0;
        for(int idx = 0; idx < dimension; ++idx) {
            tally += values[idx];
        }
        return tally;
    }

    boolean isMagic() {
        final int sum = getSum();

        // row tallies after the first one
        int idx = dimension;
        while(idx < values.length) {
            int tally = 0;
            for(int v = 0; v < dimension; ++v) {
                tally += values[idx++];
            }
            if(sum != tally) return false;
        }

        // column tallies
        for(int col = 0; col < dimension; ++col) {
            int tally = 0;
            for(idx = col; idx < values.length; idx += dimension) {
                tally += values[idx];
            }
            if(sum != tally) return false;
        }

        // diagonal from 0 tally
        int tally = 0;
        for(idx = 0; idx < values.length; idx += (dimension + 1)) {
            tally += values[idx];
        }
        if(sum != tally) return false;

        // diagonal from (dimension-1) tally
        tally = 0;
        for(int count = 0, didx = dimension-1; count < dimension; ++count, didx += dimension - 1) {
            tally += values[didx];
        }
        if(sum != tally) return false;

        // now make sure it is made of numbers 1 .. (dim*dim)
        final var bset = new BitSet();
        bset.set(0);
        for(idx = 0; idx < values.length; ++idx) bset.set(values[idx]);
        if(bset.nextClearBit(0) != (dimension*dimension+1)) {
            return false;
        }
        return true;
    }

    void display() {
        for(int y = 0; y < dimension; ++y) {
            for(int x = 0; x < dimension; ++x) {
                System.out.printf("%d, ", get(x,y));
            }
            System.out.println();
        }
    }
}

public class msquare {
    public static void main(String[] args) {
        System.out.println("hello! ...");
        Square s = null;
        for(int round = 0; round < 5; ++round) {
            if(s != null) {
                s = new Square(s);
            } else {
                s = new Square();
            }

            System.out.printf("***** S has dimension %d, and sum %d\n", s.getDimension(), s.getSum());
            if(s.isMagic()) {
                System.out.println("S is magic!");
            }
            s.display();
            System.out.println();
        }
    }
}