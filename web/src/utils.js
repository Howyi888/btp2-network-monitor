const TIME_MODULUS = [ 60, 60, 24, 0 ]
const TIME_UNITS = [ 's', 'm', 'h', 'd']

function strfdelta(secs: float) : String {
    if (secs < 0) {
        return strfdelta(-secs);
    }
    if (secs < 1.0) {
        return String(secs)
    }
    let s: String = '';
    let remainder = 0|secs;
    TIME_MODULUS.forEach((mod, i) => {
        let value = remainder;
        if (mod>0) {
            value = remainder % mod;
            remainder = (remainder / mod)|0;
        }
        if (value>0) {
            s = String(value)+TIME_UNITS[i]+" "+s
        }
    });
    return s;
}

export { strfdelta };