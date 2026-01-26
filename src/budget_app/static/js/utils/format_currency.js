// def format_float_to_usd(num):
//     return f"${num:,.2f}"

function formatFloatToUSD(num) {
  return `$${num.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,')}`;
}
