function isVisible(n) {
    let r = n.getBoundingClientRect();
    return window.getComputedStyle(n).display != 'none' &&
        !(r.top + r.height < 0 ||
            r.left + r.width < 0 ||
            r.top > window.innerHeight ||
            r.left > window.innerWidth);
}

function getAllVisibleElements() {
    return Array.from(document.querySelectorAll("div, a, span, li, p")).filter(
        n => isVisible(n));
}

function randomCssColor() {
    return 'rgb(' + parseInt(Math.random() * 255) + ','
        + parseInt(Math.random() * 255) + ','
        + parseInt(Math.random() * 255) + ')';
}

function tamperShowSomethingAdditional() {
    let n = document.createElement("div");
    n.style.position = 'absolute';
    let height = 100 + Math.random() * 200;
    let width = 100 + Math.random() * 200;
    let top = Math.random() * (window.innerHeight - height);
    let left = Math.random() * (window.innerWidth - width);
    n.style.top = top + "px";
    n.style.left = left + "px";
    n.style.bottom = top + height + "px";
    n.style.right = left + width + "px";
    n.style.border = "solid 2px black";
    n.style.minWidth = width + "px";
    n.style.minHeight = height + "px";
    n.style.backgroundColor = randomCssColor();
    n.style.color = randomCssColor();
    n.innerText = "Lorem Ipsum Sit Dolor";
    document.querySelector("body").appendChild(n);
}

function tamperAddRandomPadding() {
    getAllVisibleElements().forEach(function (e) {
        // With a 0.8 probability, add up to 4px of padding to a random side.
        if (Math.random() > 0.2) {
            let x = parseInt(Math.random() * 4);
            let rndPad = parseInt(Math.random() * 4) + "px";
            if (x == 0) {
                e.style.paddingLeft = rndPad;
            } else if (x == 1) {
                e.style.paddingBottom = rndPad;
            } else if (x == 2) {
                e.style.paddingRight = rndPad;
            } else if (x == 3) {
                e.style.paddingTop = rndPad;
            }
        }
    });
}

function tamperAddText() {
    getAllVisibleElements().forEach(function(e) {
        // 50% chance of the inner text of an element to get an extra char.
            if (Math.random() > 0.5) {
                let randomChar =  String.fromCharCode(parseInt(Math.random() * 256));
                e.innerHTML = e.innerHTML + randomChar;
            }
    });
}