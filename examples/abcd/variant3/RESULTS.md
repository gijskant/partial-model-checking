## Original MCRL: exampleXY.mcrl2

X = a.b1.X
Z(n) = (n=0) -> c.Y
       + (n>0) -> t.Z(n-1)
Y = b2.Z(3)
init X || Y

## Original LPS: exampleXY.lps

proc P(x,y:Pos, n: Nat) =
        (x == 1)        	       	-> a . P(2,y,n)
     + (x == 2 && y == 1) -> b . P(1,2,3)
     + (n == 0 && y == 2) -> c . P(x,1,0)
     + (0 < n && y == 2)    -> t . P(x,2,n-1)
init P(1,1,0);

## Original formula: reach.mes

mu X = <c>true || <true>X;
init X;

## Original PBES: example.reach.pbes

pbes mu X(x,y:Pos, n: Nat) =
       val(x == 1)     	     	    && X(2,y, n)
    || val(x == 2 && y == 1)  && X(1,2, 3);
    || val(0 < n && y == 2)    && X(x,2, n - 1)
    || val(n == 0 && y == 2)  && X(x,1, 0)
    || val(n == 0 && y == 2)
init X(1,1, 0);

## PBES after quotienting from Y_1.lps (example.reachY.pp):

pbes mu X(x,y: Pos, n: Nat) =
        val(x == 2)     	  	     	      && X(1, y, n);
    || val(x == 1) && val(y == 1) && X(2, 2, 3)
    || val(y == 2 && 0 < n)    	  && X(x, 2, n - 1)
    || val(y == 2 && n == 0) 	  && X(x, 1, 0)
    || val(y == 2 && n == 0)
 init X(2, 1, 0);

## PBES after quotienting from X_1.lps:

pbes mu X(x:Pos, y: Pos, n: Nat, x: Pos) =
       val(x == 1)    	       	     	  && X(y, n, 2)
    || val(y == 1) && val(x == 2) && X(2, 3, 1)
    || val(y == 2 && 0 < n) 	  && X(2, n - 1, x)
    || val(y == 2 && n == 0) 	  && X(1, 0, x);
    || val(y == 2 && n == 0)
 init X(1, 0, 1);

## CONCLUSION

When quotienting from X_1, nothing has changed at all, it seems.

When quotienting from Y_1, the initial state has "advanced" in process X somehow.
(This is visible in the updated initial value 2).
