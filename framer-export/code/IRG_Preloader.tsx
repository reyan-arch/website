import { useCallback, useEffect, useState, type CSSProperties } from "react"
import { createPortal } from "react-dom"
import { addPropertyControls, ControlType, useIsStaticRenderer } from "framer"

interface Props { background?: string; ground?: string; style?: CSSProperties }
const LOGO = `<svg xmlns="http://www.w3.org/2000/svg" style="display:block;width:100%;height:auto" viewBox="0 0 88 28" role="img" aria-labelledby="title">
  <title id="title">IRG</title>
  <g fill="#ff3436"><circle cx="4" cy="6" r="4"/><rect x="0" y="12" width="8" height="16" rx="4"/></g>
  <g fill="#191c1f"><circle cx="14" cy="4" r="4"/><rect x="10" y="10" width="8" height="18" rx="4"/></g>
  <g fill="#0037fb"><circle cx="24" cy="6" r="4"/><rect x="20" y="12" width="8" height="16" rx="4"/></g>
  <g transform="translate(36 24.206) scale(.028 -.028)" fill="#191c1f"><path transform="translate(0 0)" d="M223.601 0H83.999V729H223.601Z"/><path transform="translate(268 0)" d="M83.999 0V729H443.2Q518.2 729 572.8 705.3Q627.4 681.6 657 636.7Q686.6 591.8 686.6 527.6Q686.6 461.399 650.6 414.299Q614.6 367.199 555 349.599L551.8 353.6Q596.8 343.8 622.6 325.2Q648.4 306.6 659.5 279.5Q670.6 252.4 670.6 215V73.2Q670.6 47.6 677.7 35.7Q684.8 23.8 693.4 18.6V0H544.998Q538.398 8.8 534.898 25Q531.398 41.199 531.398 71.999V191.799Q531.398 243.399 506.798 267.099Q482.199 290.799 433.399 290.799H223.601V0ZM223.601 400.6H419.199Q478.799 400.6 509.698 428.9Q540.598 457.2 540.598 506.599Q540.598 558.399 509.498 585.099Q478.399 611.798 420.999 611.798H223.601Z"/><path transform="translate(971 0)" d="M364.4 -9.6Q261.8 -9.6 189.4 35.5Q117 80.6 78.8 164.2Q40.6 247.8 40.6 363.8Q40.6 482 83.3 565.7Q126 649.4 205.6 694Q285.2 738.6 395 738.6Q486.4 738.6 555.701 709Q625.001 679.4 668.001 623.9Q711.001 568.4 722.801 488.8L582.399 469.999Q570.599 542.799 519.799 580.299Q469 617.798 394.8 617.798Q287.601 617.798 236.301 549.899Q185.002 481.999 185.002 363Q185.002 237.6 237.902 173.001Q290.801 108.401 387.8 108.401Q441 108.401 483.699 129.201Q526.399 150.001 552.599 188.5Q578.799 227 581.199 278.199H403.8V388.6H731.401V0H619.399L607.399 122.799Q590.599 82.199 554.099 52.4Q517.6 22.6 468.6 6.5Q419.6 -9.6 364.4 -9.6Z"/></g>
</svg>`

/** Full, crisp identity; never lock scrolling or hide navigation artwork. */
function Overlay({ onDone }: { onDone: () => void }) {
    useEffect(() => {
        const timer = window.setTimeout(onDone, 1200)
        const reduced = window.matchMedia("(prefers-reduced-motion: reduce)")
        const preference = () => { if (reduced.matches) onDone() }
        const visibility = () => { if (document.hidden) onDone() }
        reduced.addEventListener("change", preference)
        document.addEventListener("visibilitychange", visibility)
        document.addEventListener("pointerdown", onDone, { passive: true })
        document.addEventListener("keydown", onDone)
        window.addEventListener("scroll", onDone, { passive: true })
        window.addEventListener("pagehide", onDone)
        return () => {
            window.clearTimeout(timer)
            reduced.removeEventListener("change", preference)
            document.removeEventListener("visibilitychange", visibility)
            document.removeEventListener("pointerdown", onDone)
            document.removeEventListener("keydown", onDone)
            window.removeEventListener("scroll", onDone)
            window.removeEventListener("pagehide", onDone)
        }
    }, [onDone])
    return <div data-irg-native-intro="true" aria-hidden="true" style={{ position: "fixed", inset: 0, zIndex: 9999, background: "#fff", display: "grid", placeItems: "center", pointerEvents: "none", animation: "irg-clear-intro 1.2s ease-out both" }}>
        <style>{`@keyframes irg-clear-intro { 0%,70% { opacity:1 } 100% { opacity:0 } } @media (prefers-reduced-motion:reduce) { [data-irg-native-intro] { display:none!important;animation:none!important } }`}</style>
        <div style={{ width: "clamp(240px, 24vw, 320px)", maxWidth: "80vw", lineHeight: 0 }} dangerouslySetInnerHTML={{ __html: LOGO }} />
    </div>
}

/** @framerIntrinsicWidth 120
 * @framerIntrinsicHeight 40
 * @framerSupportedLayoutWidth any-prefer-fixed
 * @framerSupportedLayoutHeight any-prefer-fixed */
export default function IRGPreloader(props: Props) {
    const isStatic = useIsStaticRenderer()
    const [mounted, setMounted] = useState(false)
    const [done, setDone] = useState(false)
    const finish = useCallback(() => setDone(true), [])
    useEffect(() => { setMounted(true) }, [])
    const hasBrandLayer = typeof window !== "undefined" && (window as Window & { __irgBrandUpdates?: boolean }).__irgBrandUpdates
    const skip = isStatic || hasBrandLayer || done || !mounted || (typeof window !== "undefined" && (window.location.hash || window.scrollY > 24 || window.matchMedia("(prefers-reduced-motion: reduce)").matches))
    return <div style={{ ...props.style, position: "relative", pointerEvents: "none" }}>
        {!skip && typeof document !== "undefined" ? createPortal(<Overlay onDone={finish} />, document.body) : null}
    </div>
}
addPropertyControls(IRGPreloader, { background: { type: ControlType.Color, title: "Ground", defaultValue: "#fff" } })
