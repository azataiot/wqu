window.MathJax = {
    tex: {
        inlineMath: [["$", "$"], ["\\(", "\\)"]],
        displayMath: [["\\[", "\\]"], ["$$", "$$"]],
        processEscapes: true,
        processEnvironments: true
    },
    options: {
        ignoreHtmlClass: ".*|",
        processHtmlClass: "arithmatex"
    }
};

// noinspection JSUnresolvedVariable, JSIgnoredPromiseFromCall, JSUnresolvedReference
/**
 * @typedef {Object} MathJaxObject
 * @property {Object} startup
 * @property {function} startup.output.clearCache
 * @property {function} typesetClear
 * @property {function} texReset
 * @property {function} typesetPromise
 */
document$.subscribe(() => {
    MathJax.startup.output.clearCache();
    MathJax.typesetClear();
    MathJax.texReset();
    MathJax.typesetPromise();
})
