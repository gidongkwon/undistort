#set page(paper: "a4")

#grid(
  fill: (x, y) => rgb(
    if calc.odd(x + y) { "000000" }
    else { "FFFFFF" }
  ),
  columns: (2cm,) * 8,
  rows: (2cm,) * 10,
)