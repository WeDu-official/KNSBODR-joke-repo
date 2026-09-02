"""
Popular Math Equations
A reference collection of well-known mathematical formulas and equations.
"""

EQUATIONS = {
    # Arithmetic / Algebra
    "quadratic_formula": r"x = (-b ± √(b² - 4ac)) / (2a)",
    "distance_formula": r"d = √((x₂ - x₁)² + (y₂ - y₁)²)",
    "slope": r"m = (y₂ - y₁) / (x₂ - x₁)",
    "point_slope": r"y - y₁ = m(x - x₁)",
    "arithmetic_sequence": r"aₙ = a₁ + (n - 1)d",
    "geometric_sequence": r"aₙ = a₁rⁿ⁻¹",
    "sum_arithmetic": r"Sₙ = n(a₁ + aₙ) / 2",
    "sum_geometric": r"Sₙ = a₁(1 - rⁿ) / (1 - r)",

    # Geometry
    "pythagorean_theorem": r"a² + b² = c²",
    "circle_area": r"A = πr²",
    "circle_circumference": r"C = 2πr",
    "sphere_volume": r"V = 4πr³ / 3",
    "sphere_surface_area": r"A = 4πr²",
    "cylinder_volume": r"V = πr²h",
    "cone_volume": r"V = πr²h / 3",
    "triangle_area": r"A = bh / 2",
    "herons_formula": r"A = √(s(s-a)(s-b)(s-c))",

    # Trigonometry
    "sine": r"sin(θ) = opposite / hypotenuse",
    "cosine": r"cos(θ) = adjacent / hypotenuse",
    "tangent": r"tan(θ) = opposite / adjacent",
    "law_of_sines": r"a/sin(A) = b/sin(B) = c/sin(C)",
    "law_of_cosines": r"c² = a² + b² - 2ab cos(C)",
    "trig_identity": r"sin²(θ) + cos²(θ) = 1",

    # Calculus
    "power_rule": r"d/dx(xⁿ) = nxⁿ⁻¹",
    "product_rule": r"(fg)' = f'g + fg'",
    "quotient_rule": r"(f/g)' = (f'g - fg') / g²",
    "chain_rule": r"d/dx f(g(x)) = f'(g(x))g'(x)",
    "fundamental_theorem_calculus": r"∫ₐᵇ f(x)dx = F(b) - F(a)",
    "derivative_exponential": r"d/dx(eˣ) = eˣ",
    "derivative_log": r"d/dx(ln x) = 1/x",

    # Exponents / Logarithms
    "exponential_definition": r"eˣ = Σₙ₌₀∞ xⁿ/n!",
    "change_of_base": r"log_b(x) = ln(x) / ln(b)",
    "log_product": r"log_b(xy) = log_b(x) + log_b(y)",
    "log_power": r"log_b(xⁿ) = n log_b(x)",

    # Probability / Statistics
    "mean": r"x̄ = Σxᵢ / n",
    "variance_population": r"σ² = Σ(xᵢ - μ)² / N",
    "standard_deviation": r"σ = √σ²",
    "z_score": r"z = (x - μ) / σ",
    "binomial_probability": r"P(X=k) = C(n,k)pᵏ(1-p)ⁿ⁻ᵏ",
    "combinations": r"C(n,k) = n! / (k!(n-k)!)",
    "permutations": r"P(n,k) = n! / (n-k)!",

    # Famous constants / identities
    "eulers_identity": r"eⁱᵖ + 1 = 0",
    "eulers_formula": r"eⁱˣ = cos(x) + i sin(x)",
    "euler_characteristic": r"V - E + F = 2",
    "golden_ratio": r"φ = (1 + √5) / 2",

    # Number theory
    "prime_counting_approximation": r"π(n) ≈ n / ln(n)",
    "euclidean_algorithm": r"gcd(a,b) = gcd(b, a mod b)",

    # Physics / Mathematical physics
    "newtons_second_law": r"F = ma",
    "einstein_mass_energy": r"E = mc²",
    "newtons_gravity": r"F = Gm₁m₂ / r²",
    "coulombs_law": r"F = kq₁q₂ / r²",
    "wave_equation": r"v = fλ",
    "ideal_gas_law": r"PV = nRT",
    "heat_energy": r"Q = mcΔT",
    "kinetic_energy": r"K = mv² / 2",
    "potential_energy": r"U = mgh",

    # Famous mathematical equations
    "einstein_field_equations": r"Gμν + Λgμν = (8πG/c⁴)Tμν",
    "schrodinger_equation": r"iℏ ∂ψ/∂t = Ĥψ",
    "fourier_transform": r"F(ω) = ∫₋∞∞ f(t)e⁻ⁱωᵗ dt",
    "heat_equation": r"∂u/∂t = α∇²u",
    "laplace_equation": r"∇²φ = 0",
}

if __name__ == "__main__":
    for name, equation in EQUATIONS.items():
        print(f"{name:32} {equation}")
