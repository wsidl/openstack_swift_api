const sizes = ["", "K", "M", "G", "T", "E", "Z"];
const kilo = 1024;

export default function humanReadable(size: number, depth=0): string {
  if(isNaN(size)) return '';
  if(size < kilo) return `${size.toFixed(depth > 0 ? 2 : 0)} ${sizes[depth]}B`;
  return humanReadable(size / kilo, depth+1);
}
