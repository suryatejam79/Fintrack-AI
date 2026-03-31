class target:
    def __init__(self,email):
        self.email = email
        pass

    def monthly_target(self):
        d = 0
        am = 0
        mi = 0
        g = 0
        t =0
        mf = 0
        lep = 0
        r = 0
        b =0
        f = 0
        en = 0
        ed = 0
        es = 0
        m = 0
        i = mi+am 
        e = g+t+mf+lep+r+b+f+en+ed+es+m
        n = i-e
        fd = 1-min(0.03*d,0.18)
        nd = n.fd 
        if n/i<0.15:
            b = 0.30
        elif n/i<0.30:
            b = 0.2
        else:
            b = 0.1
        s0 = nd(1-b)
        ef = lep+r+b+mf+ed 
        rf = ef/i 
        if rf>=0.60:
            ff=0.85
        elif rf>=0.40:
            ff=0.92
        else:
            ff = 1.00
        s1 = s0*ff 
        
