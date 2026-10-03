import { useCallback, useEffect, useRef, useState, type CSSProperties } from "react"
import { createPortal } from "react-dom"
import { addPropertyControls, ControlType, useIsStaticRenderer } from "framer"

interface Props { background?: string; ground?: string; style?: CSSProperties }
const INK = "#191C1F"
const EASE = "cubic-bezier(.645,.045,.355,1)"
const cloneProperties = ["display","position","box-sizing","width","height","min-width","min-height","max-width","max-height","flex-direction","align-items","justify-content","gap","flex-shrink","padding","margin","border","border-radius","background-color","color","font-family","font-size","font-weight","font-variation-settings","font-feature-settings","line-height","letter-spacing","white-space","text-align"]

function visualBounds(rects: DOMRect[]) {
    const left = Math.min(...rects.map(r => r.left))
    const top = Math.min(...rects.map(r => r.top))
    const right = Math.max(...rects.map(r => r.right))
    const bottom = Math.max(...rects.map(r => r.bottom))
    return { left, top, width: right - left, height: bottom - top }
}

function flightTransform(rect: { left: number; top: number; width: number; height: number }, width: number, height: number) {
    return `translate(${rect.left + rect.width / 2 - width / 2}px, ${rect.top + rect.height / 2 - height / 2}px) scale(1)`
}

// Freeze only the visible artwork, never the padded navigation link/tap target.
function copyArtwork(source: HTMLElement): HTMLElement {
    const copy = source.cloneNode(true) as HTMLElement
    const originals = [source, ...Array.from(source.querySelectorAll<HTMLElement>("*"))]
    const copies = [copy, ...Array.from(copy.querySelectorAll<HTMLElement>("*"))]
    originals.forEach((element, i) => {
        const target = copies[i]
        const computed = getComputedStyle(element)
        target.removeAttribute("id")
        target.removeAttribute("class")
        target.removeAttribute("href")
        target.removeAttribute("tabindex")
        target.removeAttribute("data-framer-name")
        target.style.cssText = ""
        cloneProperties.forEach(property => target.style.setProperty(property, computed.getPropertyValue(property)))
        target.style.transform = "none"
        target.style.transition = "none"
        target.style.animation = "none"
        target.style.opacity = "1"
        target.style.pointerEvents = "none"
    })
    return copy
}

function Overlay({ background, onDone }: { background: string; onDone: () => void }) {
    const rootRef = useRef<HTMLDivElement>(null)
    const logoRef = useRef<HTMLDivElement>(null)
    const fillRef = useRef<HTMLDivElement>(null)
    const groundRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        let active = true
        let restored = false
        let target: HTMLElement | null = null
        let oldOpacity = ""
        let frame = 0
        let timeout = 0
        const animations: Animation[] = []
        const body = document.body
        const html = document.documentElement
        const original = { overflow: body.style.overflow, gutter: html.style.scrollbarGutter, padding: body.style.paddingRight }
        const scrollbar = window.innerWidth - html.clientWidth
        if (CSS.supports("scrollbar-gutter", "stable")) html.style.scrollbarGutter = "stable"
        else if (scrollbar > 0) body.style.paddingRight = `${parseFloat(getComputedStyle(body).paddingRight) + scrollbar}px`
        body.style.overflow = "hidden"

        const restore = () => {
            if (restored) return
            restored = true
            if (target) target.style.opacity = oldOpacity
            body.style.overflow = original.overflow
            body.style.paddingRight = original.padding
            html.style.scrollbarGutter = original.gutter
        }
        const finish = () => {
            if (!active) return
            active = false
            if (rootRef.current) rootRef.current.style.display = "none"
            animations.forEach(a => a.cancel())
            cancelAnimationFrame(frame)
            clearTimeout(timeout)
            restore()
            onDone()
        }
        const animate = (element: HTMLElement, keyframes: Keyframe[], options: KeyframeAnimationOptions) => {
            const animation = element.animate(keyframes, { fill: "forwards", ...options })
            animations.push(animation)
            return animation.finished.catch(() => undefined)
        }
        const fade = async () => {
            if (rootRef.current) await animate(rootRef.current, [{ opacity: 1 }, { opacity: 0 }], { duration: 180 })
            finish()
        }
        const find = () => Array.from(document.querySelectorAll<HTMLElement>('nav [data-framer-name="IRG Logo"]')).find(node => {
            const rect = node.getBoundingClientRect()
            return rect.width > 20 && rect.height > 10 && node.getClientRects().length > 0 && getComputedStyle(node).visibility !== "hidden"
        })
        const ready = async () => {
            const deadline = performance.now() + 800
            let previous = ""
            while (active && performance.now() < deadline) {
                const node = find()
                const parts = node ? Array.from(node.children).filter((el): el is HTMLElement => el instanceof HTMLElement && el.getBoundingClientRect().width > 0) : []
                const text = node?.querySelector<HTMLElement>(".framer-text")
                if (node && parts.length >= 2 && text) {
                    const font = getComputedStyle(text)
                    const fontSpec = `${font.fontWeight} ${font.fontSize} ${font.fontFamily}`
                    if (!document.fonts.check(fontSpec)) void document.fonts.load(fontSpec).catch(() => undefined)
                    else {
                        const rect = visualBounds(parts.map(p => p.getBoundingClientRect()))
                        const key = [rect.left, rect.top, rect.width, rect.height].map(n => Math.round(n * 4)).join(":")
                        if (key === previous) return { node, parts, rect }
                        previous = key
                    }
                }
                await new Promise<void>(resolve => { frame = requestAnimationFrame(() => resolve()) })
            }
            return null
        }
        const run = async () => {
            const destination = await ready()
            if (!active) return
            if (!destination || !logoRef.current || !fillRef.current || !groundRef.current) { await fade(); return }
            target = destination.node
            oldOpacity = target.style.opacity
            const { rect, parts } = destination
            const logo = logoRef.current
            const fill = fillRef.current
            const artwork = document.createElement("div")
            Object.assign(artwork.style, { position: "relative", width: `${rect.width}px`, height: `${rect.height}px` })
            parts.forEach(part => {
                const bounds = part.getBoundingClientRect()
                const copy = copyArtwork(part)
                Object.assign(copy.style, { position: "absolute", left: `${bounds.left - rect.left}px`, top: `${bounds.top - rect.top}px`, margin: "0" })
                artwork.appendChild(copy)
            })
            const base = artwork.cloneNode(true) as HTMLElement
            base.style.opacity = ".14"
            logo.insertBefore(base, fill)
            fill.replaceChildren(artwork)
            const textNodes = Array.from(logo.querySelectorAll<HTMLElement>("*")).filter(el => Array.from(el.childNodes).some(n => n.nodeType === Node.TEXT_NODE && n.textContent?.trim()))
            const destinationColors = textNodes.map(el => el.style.color)
            textNodes.forEach(el => el.style.color = INK)
            const scale = Math.min(96, Math.max(44, window.innerWidth * .06)) / rect.height
            Object.assign(logo.style, { width: `${rect.width}px`, height: `${rect.height}px`, left: `${window.innerWidth / 2 - rect.width / 2}px`, top: `${window.innerHeight / 2 - rect.height / 2}px`, transform: `scale(${scale})`, opacity: "1" })
            target.style.opacity = "0"
            await animate(fill, [{ clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)" }], { duration: 1350, delay: 150, easing: "cubic-bezier(.455,.03,.515,.955)" })
            if (!active || !target.isConnected) { finish(); return }
            // One measurement after the fill; none during the transform flight.
            const end = visualBounds(parts.map(p => p.getBoundingClientRect()))
            if (Math.abs(end.width - rect.width) > .5 || Math.abs(end.height - rect.height) > .5) { await fade(); return }
            const flight = animate(logo, [{ transform: `scale(${scale})` }, { transform: flightTransform(end, window.innerWidth, window.innerHeight) }], { duration: 1050, easing: EASE })
            const ground = animate(groundRef.current, [{ transform: "translateY(0)" }, { transform: "translateY(-100%)" }], { duration: 1050, easing: EASE })
            const real = animate(target, [{ opacity: 0 }, { opacity: 1 }], { duration: 120, delay: 930 })
            const copy = animate(logo, [{ opacity: 1 }, { opacity: 0 }], { duration: 120, delay: 930 })
            const colors = textNodes.map((el, i) => animate(el, [{ color: INK }, { color: destinationColors[i] || INK }], { duration: 120, delay: 930 }))
            await Promise.all([flight, ground, real, copy, ...colors])
            finish()
        }
        const removed = new MutationObserver(() => { if (target && !target.isConnected) finish() })
        removed.observe(document.body, { childList: true, subtree: true })
        const reduced = window.matchMedia("(prefers-reduced-motion: reduce)")
        const preference = () => { if (reduced.matches) finish() }
        reduced.addEventListener("change", preference)
        const visibility = () => { if (document.hidden) finish() }
        const navigate = (event: MouseEvent) => { if ((event.target as Element)?.closest?.("a[href]")) finish() }
        window.addEventListener("resize", finish)
        window.addEventListener("popstate", finish)
        window.addEventListener("hashchange", finish)
        window.addEventListener("pagehide", finish)
        document.addEventListener("visibilitychange", visibility)
        document.addEventListener("click", navigate, true)
        // A final bound covers detached targets, animation failures and throttled frames.
        timeout = window.setTimeout(finish, 4000)
        void run().catch(finish)
        return () => {
            active = false
            animations.forEach(a => a.cancel())
            cancelAnimationFrame(frame)
            clearTimeout(timeout)
            restore()
            removed.disconnect()
            reduced.removeEventListener("change", preference)
            window.removeEventListener("resize", finish)
            window.removeEventListener("popstate", finish)
            window.removeEventListener("hashchange", finish)
            window.removeEventListener("pagehide", finish)
            document.removeEventListener("visibilitychange", visibility)
            document.removeEventListener("click", navigate, true)
        }
    }, [onDone])

    return <div ref={rootRef} data-irg-preloader="true" aria-hidden="true" style={{ position: "fixed", inset: 0, zIndex: 9999, pointerEvents: "auto" }}>
        <div ref={groundRef} style={{ position: "absolute", inset: 0, background, willChange: "transform" }} />
        <div ref={logoRef} style={{ position: "absolute", opacity: 0, transformOrigin: "center", willChange: "transform, opacity" }}>
            <div ref={fillRef} style={{ position: "absolute", inset: 0, clipPath: "inset(0 100% 0 0)" }} />
        </div>
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
    const skip = isStatic || done || !mounted || (typeof window !== "undefined" && (window.location.pathname.replace(/\/$/, "") === "/home-video" || window.matchMedia("(prefers-reduced-motion: reduce)").matches))
    return <div style={{ ...props.style, position: "relative", pointerEvents: "none" }}>
        {!skip && typeof document !== "undefined" ? createPortal(<Overlay background={props.background || props.ground || "#f2f2f2"} onDone={finish} />, document.body) : null}
    </div>
}
addPropertyControls(IRGPreloader, { background: { type: ControlType.Color, title: "Ground", defaultValue: "#f2f2f2" } })
