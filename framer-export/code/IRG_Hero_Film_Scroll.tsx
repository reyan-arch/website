import * as React from "react"
import type { ComponentType } from "react"
import { useReducedMotion } from "framer-motion"

export function withHeroFilmScrollReveal(Component: ComponentType<any>): ComponentType<any> {
    return React.forwardRef(function HeroFilmScrollReveal(props, forwardedRef) {
        const rootRef = React.useRef<HTMLElement | null>(null)
        const reduceMotion = useReducedMotion()
        const [scale, setScale] = React.useState(reduceMotion ? 1 : 0.22)

        const setRef = React.useCallback((node: HTMLElement | null) => {
            rootRef.current = node
            if (typeof forwardedRef === "function") forwardedRef(node)
            else if (forwardedRef) (forwardedRef as React.MutableRefObject<HTMLElement | null>).current = node
        }, [forwardedRef])

        React.useEffect(() => {
            if (reduceMotion) {
                setScale(1)
                return
            }
            let frame = 0
            const update = () => {
                frame = 0
                const root = rootRef.current
                const section = root?.closest<HTMLElement>('[data-framer-name="Hero Film — Scroll Zoom"]')
                if (!section) return
                const start = window.scrollY + section.getBoundingClientRect().top
                const progress = Math.min(1, Math.max(0, (window.scrollY - start) / (window.innerHeight * 2)))
                setScale(0.22 + progress * 0.78)
            }
            const onScroll = () => {
                if (!frame) frame = requestAnimationFrame(update)
            }
            update()
            window.addEventListener("scroll", onScroll, { passive: true })
            window.addEventListener("resize", onScroll)
            return () => {
                window.removeEventListener("scroll", onScroll)
                window.removeEventListener("resize", onScroll)
                if (frame) cancelAnimationFrame(frame)
            }
        }, [reduceMotion])

        return <Component {...props} ref={setRef} style={{ ...props.style, transform: "scale(" + scale + ")", transformOrigin: "center center" }} />
    })
}
