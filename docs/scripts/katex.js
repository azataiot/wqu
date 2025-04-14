// noinspection JSUnresolvedVariable, JSIgnoredPromiseFromCall, JSUnresolvedReference
/**
 * @typedef {function} RenderMathFunction
 * @param {HTMLElement} element - DOM element to render math in
 * @param {Object} options - KaTeX rendering options
 */
document$.subscribe(({ body }) => {
  renderMathInElement(body, {
    delimiters: [
      { left: "$$",  right: "$$",  display: true },
      { left: "$",   right: "$",   display: false },
      { left: "\\(", right: "\\)", display: false },
      { left: "\\[", right: "\\]", display: true }
    ],
  })
})