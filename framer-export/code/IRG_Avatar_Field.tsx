import * as React from "react"
import { useIsStaticRenderer } from "framer"
import { useReducedMotion } from "framer-motion"

type Avatar = [number, number, number, number, number, string, string]

const avatars: Avatar[] = [
    [17, 18, 92, -1, -1, "https://framerusercontent.com/images/kZBD0dO5DHJnnYTA28CqYvoPE.jpg", "28% 45%"],
    [7, 52, 136, -1, 0, "https://framerusercontent.com/images/jzZBfSd5pYnek6qcWYGnxt6dH1E.jpg", "70% 42%"],
    [18, 82, 102, -1, 1, "https://framerusercontent.com/images/zMtJKZOZ8yy0hY1mWqPwJMk9irw.jpg", "50% 45%"],
    [83, 24, 92, 1, -1, "https://framerusercontent.com/images/jzZBfSd5pYnek6qcWYGnxt6dH1E.jpg", "32% 42%"],
    [93, 58, 136, 1, .2, "https://framerusercontent.com/images/kZBD0dO5DHJnnYTA28CqYvoPE.jpg", "68% 42%"],
    [82, 84, 92, 1, 1, "https://framerusercontent.com/images/zMtJKZOZ8yy0hY1mWqPwJMk9irw.jpg", "74% 48%"],
]

/**
 * @framerSupportedLayoutWidth any
 * @framerSupportedLayoutHeight any
 */
export default function IRGAvatarField(props: React.HTMLAttributes<HTMLDivElement>) {
    const root = React.useRef<HTMLDivElement>(null)
    const staticRenderer = useIsStaticRenderer()
    const reduceMotion = useReducedMotion()

    React.useEffect(() => {
        const node = root.current
        if (!node) return
        const items = node.querySelectorAll("[data-avatar]")
        let frame = 0
        const draw = () => {
            frame = 0
            const p = staticRenderer || reduceMotion ? 0 : Math.min(Math.max(-node.getBoundingClientRect().top / (window.innerHeight * .7), 0), 1)
            items.forEach((item, index) => {
                const avatar = avatars[index]
                const image = item as HTMLImageElement
                image.style.transform = `translate(-50%, -50%) translate(${avatar[3] * 220 * p}px, ${avatar[4] * 220 * p}px)`
                image.style.opacity = String(1 - p)
                image.style.filter = `drop-shadow(0 14px 30px rgba(34,61,254,.16)) blur(${12 * p}px)`
            })
        }
        const update = () => { if (!frame) frame = requestAnimationFrame(draw) }
        draw()
        window.addEventListener("scroll", update, { passive: true })
        window.addEventListener("resize", update)
        return () => {
            window.removeEventListener("scroll", update)
            window.removeEventListener("resize", update)
            if (frame) cancelAnimationFrame(frame)
        }
    }, [staticRenderer, reduceMotion])

    return <div ref={root} aria-hidden="true" style={{ ...props.style, position: "relative", width: "100%", height: "100%", pointerEvents: "none" }}>
        {avatars.map((avatar, index) => <img key={index} data-avatar="" src={avatar[5]} alt="" style={{
            position: "absolute", left: avatar[0] + "%", top: avatar[1] + "%",
            width: `clamp(72px, ${avatar[2] / 12.8}vw, ${avatar[2]}px)`, aspectRatio: "1",
            borderRadius: "50%", objectFit: "cover", objectPosition: avatar[6],
            transform: "translate(-50%, -50%)", willChange: "transform, filter, opacity",
        }} />)}
    </div>
}
