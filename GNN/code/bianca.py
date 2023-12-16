# Write your code here

class SparseBinaryMat(object):
    def __init__(self, m, n):
        if (not isinstance(m, int)) or (not isinstance(n, int)):
            raise TypeError("m and n must be an int")
        if (m < 0) or (n<0):
            raise ValueError("m and n must be non-negative")
        self.elements = set()
        self.m = m
        self.n = n

    def _check_index(self, i, j):
        if (not isinstance(i, int)) or (not isinstance(j, int)):
            raise TypeError("index must be an int")
        if (not (0 <= i < self.m)) or (not (0 <= j < self.n)):
            raise ValueError("index out of bounds")

    def __getitem__(self, t):
        self._check_index(t[0], t[1])
        return 1 if ((t[0], t[1]) in self.elements) else 0
    
    def count(self):
        return len(self.elements)
    
    def  _check_element(self, x):
        if x!=0 and x!=1:
            raise ValueError
       
            
    def __setitem__(self, t, x):
        self._check_element(x)
        self._check_index(*t)
        if x == 1:
            self.elements.add(t)
        elif x == 0:
            self.elements.discard(t)
            
    def to_lol(self):
        mat = [0] * self.m
        for i in range(self.m):
            mat[i] = [0]*self.n
            for j in range(self.n):
                if (i,j) in self.elements:
                    mat[i][j] = 1            
        return mat
    
    def __repr__(self):
        return f"{self.to_lol()}"
    
    def __contains__(self, x):
        if x!=0 and x!=1:
            return False
        if x == 1 and self.count() > 0:
            return True
        if x == 0 and (self.m*self.n - self.count()>0):
            return True
        return False
                              
        
    def multiply_mat(self):
        
        if self.m != self.n or self.m == 0 or self.n == 0:
            raise ValueError       
        
        #trelements = set({(j, i) for (i, j) in self.elements})
        #result_elements = set(self.elements).intersection(trelements)
        #result = SparseBinaryMat(self.m, self.n)
        #result.elements = result_elements

        result_set = set()
        for pair in self.elements:
            if pair[0] == pair[1] or (pair[1], pair[0]) in self.elements:
                result_set.add(pair)
        result = SparseBinaryMat(self.m, self.n)
        result.elements = result_set
        return result
    
a = SparseBinaryMat(2, 2)
a.elements = {(0, 0), (0, 1), (1, 0), (1, 1)}
#b = SparseBinaryMat(2, 2)
#b.elements = {(2, 2)}
print(a.multiply_mat())