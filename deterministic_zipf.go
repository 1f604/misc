// Copyright 2009 The Go Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE file.
// Modifications by 1f604.

// W.Hormann, G.Derflinger:
// "Rejection-Inversion to Generate Variates
// from Monotone Discrete Distributions"
// http://eeyore.wu-wien.ac.at/papers/96-04-04.wh-der.ps.gz

package rand

import "math"

// A Zipf generates Zipf distributed variates.
type Zipf struct {
	imax         float64
	v            float64
	q            float64
	s            float64
	oneminusQ    float64
	oneminusQinv float64
	hxm          float64
	hx0minusHxm  float64
}

func (z *Zipf) h(x float64) float64 {
	return math.Exp(z.oneminusQ*math.Log(z.v+x)) * z.oneminusQinv
}

func (z *Zipf) hinv(x float64) float64 {
	return math.Exp(z.oneminusQinv*math.Log(z.oneminusQ*x)) - z.v
}

// NewZipf returns a Zipf variate generator.
// The generator generates values k ∈ [0, imax]
// such that P(k) is proportional to (v + k) ** (-s).
// Requirements: s > 1 and v >= 1.
func NewZipf(s float64, v float64, imax uint64) *Zipf {
	z := new(Zipf)
	if s <= 1.0 || v < 1 {
		return nil
	}
	z.imax = float64(imax)
	z.v = v
	z.q = s
	z.oneminusQ = 1.0 - z.q
	z.oneminusQinv = 1.0 / z.oneminusQ
	z.hxm = z.h(z.imax + 0.5)
	z.hx0minusHxm = z.h(0.5) - math.Exp(math.Log(z.v)*(-z.q)) - z.hxm
	z.s = 1 - z.hinv(z.h(1.5)-math.Exp(-z.q*math.Log(z.v+1.0)))
	return z
}

func deterministic_rand(input Float64) Float64 { // r on [0,1]
	// TODO: implement this.
	return input
}

// Uint64 returns a value drawn from the Zipf distribution described
// by the Zipf object.
func (z *Zipf) Uint64(r Float64) uint64 { // r on [0,1]
	if z == nil {
		panic("rand: nil Zipf")
	}
	k := 0.0

	for {
		ur := z.hxm + r*z.hx0minusHxm
		x := z.hinv(ur)
		k = math.Floor(x + 0.5)
		if k-x <= z.s {
			break
		}
		if ur >= z.h(k+0.5)-math.Exp(-math.Log(k+z.v)*z.q) {
			break
		}
		r = deterministic_rand(r) 
	}
	return uint64(k)
}
