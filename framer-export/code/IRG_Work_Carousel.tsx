import { addPropertyControls, ControlType } from "framer"
import {
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
    type CSSProperties,
    type PointerEvent as ReactPointerEvent,
    type ReactNode,
} from "react"

const INK = "var(--token-4a570a1a-7395-482e-8f1d-6b4ba25d4eb1, #191C1F)"
const GRAPHITE =
    "var(--token-da4e609a-85a0-4f7d-9dd8-ce86db80916b, rgb(80, 90, 99))"
const MIST = "#F4F4F4"
const TYPE = '"BDO Grotesk Variable", "BDO Grotesk", system-ui, sans-serif'

interface StoryItem {
    image?: { src?: string; srcSet?: string; alt?: string }
    alt?: string
    lead?: string
    tail?: string
    href?: string
    cta?: string
}

const STORIES: StoryItem[] = [
    {
        image: {
            src: "https://framerusercontent.com/images/LgmK2eH476G0BAqrqHChk9sOUo.png",
            alt: "Vineyards & Voyages campaign still: a traveller checking his phone in a narrow stone passageway.",
        },
        alt: "Vineyards & Voyages campaign still: a traveller checking his phone in a narrow stone passageway.",
        lead: "84.3 million organic views for Holafly.",
        tail: "An always-on creator programme across the UK, Australia, California and Saudi Arabia.",
        href: "/work/holafly",
        cta: "SEE WORK",
    },
    {
        image: {
            src: "https://framerusercontent.com/images/CvA1p0gcnx9rVxIU6861T8G6j4.jpg",
            alt: "Reference still: a working conversation. Format example, not a client campaign.",
        },
        alt: "Reference still: a working conversation. Format example, not a client campaign.",
        lead: "Briefs, approvals, and delivery in one run",
        tail: "Format example. How IRG operates a campaign once the roster is set. No client named.",
        href: "/work/campaign-operations",
        cta: "SEE WORK",
    },
    {
        image: {
            src: "https://framerusercontent.com/images/oQutHHNrsEv6ziB0RAsjdjgLFKc.jpg",
            alt: "Reference still: people reviewing creative work. Format example, not a client campaign.",
        },
        alt: "Reference still: people reviewing creative work. Format example, not a client campaign.",
        lead: "A retained creator rhythm, not a one-off burst",
        tail: "Format example. How an always-on program would be framed for lifestyle brands.",
        href: "/work/always-on-program",
        cta: "SEE WORK",
    },
    {
        image: {
            src: "https://framerusercontent.com/images/3aiX0MgRxc2h56x5gvR1wGg4kxw.jpg",
            alt: "Reference still: a creator photographing a city. Format example, not a client campaign.",
        },
        alt: "Reference still: a creator photographing a city. Format example, not a client campaign.",
        lead: "A hospitality stay, told through the right creators",
        tail: "Format example. A travel and hospitality brief showing how a published case will sit on this rail.",
        href: "/work/hospitality-travel-brief",
        cta: "SEE WORK",
    },
]

interface IRGWorkCarouselProps {
    stories?: StoryItem[]
    contentWidth?: number
    bleedRight?: number
    mobileGap?: number
    mobilePeek?: number
    collectionList?: ReactNode[] | ReactNode
    cMSCollection?: ReactNode[] | ReactNode
    style?: CSSProperties
}

const css = `[data-irg-work-carousel]{container-type:inline-size;position:relative;width:100%;font-family:${TYPE};color:${INK};overflow-x:visible}[data-irg-work-carousel] *{box-sizing:border-box}[data-irg-work-carousel]{--sc-bleed:var(--sc-bleed-right,32px);--sc-align-left:max(8px,calc((100% - var(--sc-content,1280px)) / 2 + 8px));--sc-arrow-right:max(0px,calc((100% - var(--sc-content,1280px)) / 2))}[data-irg-work-carousel] .sc-controls{position:absolute;right:var(--sc-arrow-right);top:0;display:flex;gap:8px;z-index:2}[data-irg-work-carousel] .sc-arrow{display:grid;width:40px;height:40px;place-items:center;border:0;border-radius:999px;background:${INK};color:#fff;font:600 16px/1 ${TYPE};cursor:pointer;font-variation-settings:"wght" 600}[data-irg-work-carousel] .sc-arrow:focus-visible,[data-irg-work-carousel] .sc-link:focus-visible,[data-irg-work-carousel] .sc-viewport:focus-visible{outline:2px solid ${INK}!important;outline-offset:2px}@media(hover:hover) and (pointer:fine){[data-irg-work-carousel] .sc-arrow:hover{opacity:.86}[data-irg-work-carousel] .sc-link:hover{opacity:.72}}[data-irg-work-carousel] .sc-arrow:disabled{opacity:.18;cursor:default}[data-irg-work-carousel] .sc-viewport{position:relative;margin-left:calc(0px - var(--sc-edge-left,0px));width:calc(100% + var(--sc-edge-left,0px) + var(--sc-edge-right,0px));clip-path:inset(-4px 0 -4px var(--sc-inset,8px));overflow-x:auto;overflow-y:visible;scrollbar-width:none;-ms-overflow-style:none;scroll-snap-type:x mandatory;scroll-padding-left:var(--sc-inset,8px);overscroll-behavior-x:contain;-webkit-overflow-scrolling:touch;touch-action:pan-x pan-y;cursor:grab}[data-irg-work-carousel] .sc-viewport[data-moved="true"]{clip-path:inset(-4px 0);transition:clip-path 460ms cubic-bezier(0.16,1,0.3,1)}@media(prefers-reduced-motion:reduce){[data-irg-work-carousel] .sc-viewport[data-moved="true"]{transition:none}}[data-irg-work-carousel] .sc-viewport::-webkit-scrollbar{display:none}[data-irg-work-carousel] .sc-track{display:flex;gap:var(--sc-gap,32px);min-width:100%;width:max-content;padding:0 var(--sc-inset,8px)}[data-irg-work-carousel] .sc-card{display:flex;flex-direction:column;width:var(--sc-card-width,calc((100cqw - 96px) / 3.5));flex:none;scroll-snap-align:start;scroll-snap-stop:always}[data-irg-work-carousel] .sc-media{flex-shrink:0;position:relative;width:100%;aspect-ratio:4/5;border-radius:32px;overflow:hidden;background-size:cover;background-position:center;background:${MIST}}[data-irg-work-carousel] .sc-card img{display:block;width:100%;height:100%;object-fit:cover}[data-irg-work-carousel] .sc-card:nth-child(3) img{object-position:80% center}[data-irg-work-carousel] .sc-ph{position:absolute;inset:0;display:flex;align-items:flex-end;padding:20px;background:${INK};color:#fff;font:600 12px/1 ${TYPE};letter-spacing:.08em;text-transform:uppercase;font-variation-settings:"wght" 600}[data-irg-work-carousel] .sc-copy{flex:1;display:flex;flex-direction:column;gap:12px;padding:24px 16px 0 0}[data-irg-work-carousel] .sc-copy p{margin:0;font-size:16px;line-height:1.5;letter-spacing:0}[data-irg-work-carousel] .sc-copy h3{margin:0;font-size:20px;line-height:1.25;letter-spacing:-.02em}[data-irg-work-carousel] .sc-lead{color:${INK};font-weight:600;font-variation-settings:"wght" 600}[data-irg-work-carousel] .sc-tail{color:${GRAPHITE};font-weight:400;font-variation-settings:"wght" 400}[data-irg-work-carousel] .sc-link{margin-top:auto;align-self:flex-start;display:inline-flex;align-items:center;gap:8px;color:${INK};font-size:13px;line-height:20px;font-weight:600;font-variation-settings:"wght" 600;letter-spacing:.06em;text-transform:uppercase;text-decoration:none}@container(min-width:651px){[data-irg-work-carousel] .sc-viewport{scroll-snap-type:none}[data-irg-work-carousel] .sc-card{display:flex;flex-direction:column;scroll-snap-align:none;scroll-snap-stop:normal}[data-irg-work-carousel] .sc-media{flex-shrink:0}[data-irg-work-carousel] .sc-copy{flex:1}[data-irg-work-carousel] .sc-link{margin-top:auto;align-self:flex-start}}@container(max-width:650px){[data-irg-work-carousel]{--sc-bleed:16px;--sc-inset:0px}[data-irg-work-carousel] .sc-controls{display:none!important}[data-irg-work-carousel] .sc-viewport{margin-left:0;width:calc(100% + var(--sc-edge-right,0px));clip-path:none;scroll-padding-left:0}[data-irg-work-carousel] .sc-track{gap:var(--sc-mobile-gap,16px);padding:0 var(--sc-edge-right,0px) 0 0}[data-irg-work-carousel] .sc-card{width:var(--sc-card-width,calc((100cqw - 16px) / 1.1))}}@media(max-width:1199px){[data-irg-work-carousel] .sc-controls{display:none!important}}@media(max-width:809px){[data-irg-work-carousel] .sc-viewport{margin-left:0;width:calc(100% + var(--sc-edge-right,0px));clip-path:none;scroll-padding-left:0}[data-irg-work-carousel] .sc-track{padding:0 var(--sc-edge-right,0px) 0 0}}
[data-irg-work-carousel]{padding-top:64px}
[data-irg-work-carousel] .sc-arrow{width:44px;height:44px}
[data-irg-work-carousel] .sc-copy{gap:10px;padding:20px 0 0}
[data-irg-work-carousel] .sc-copy h3{font-family:${TYPE};font-size:24px;line-height:1.18;letter-spacing:-.02em}
[data-irg-work-carousel] .sc-copy p{font-family:${TYPE};font-size:16px;line-height:1.5}
[data-irg-work-carousel] .sc-link{font-family:${TYPE};font-size:14px;letter-spacing:.02em}
@media(max-width:1599px){[data-irg-work-carousel] .sc-copy h3{font-size:22px}}
@media(max-width:1199px){[data-irg-work-carousel]{padding-top:0}}
@media(max-width:809px){[data-irg-work-carousel] .sc-copy{padding-top:16px}[data-irg-work-carousel] .sc-copy h3{font-size:20px}}`

function hrefOf(value: unknown): string {
    if (!value) return ""
    if (typeof value === "string") return value
    if (typeof value === "object" && value !== null && "href" in value)
        return String((value as { href?: string }).href || "")
    return ""
}

function imageSrc(value: unknown, depth = 0): string {
    if (!value || depth > 6) return ""
    if (typeof value === "string") {
        const trimmed = value.trim()
        if (
            trimmed.startsWith("http") ||
            trimmed.startsWith("/") ||
            trimmed.startsWith("data:image/")
        )
            return trimmed
        return ""
    }
    if (Array.isArray(value)) {
        for (const entry of value) {
            const found = imageSrc(entry, depth + 1)
            if (found) return found
        }
        return ""
    }
    if (typeof value === "object") {
        const record = value as Record<string, unknown>
        return (
            imageSrc(record.src, depth + 1) ||
            imageSrc(record.url, depth + 1) ||
            imageSrc(record.value, depth + 1)
        )
    }
    return ""
}

function useCMSStories(collectionList?: ReactNode[] | ReactNode) {
    const sourceRef = useRef<HTMLDivElement | null>(null)
    const [stories, setStories] = useState<StoryItem[]>([])
    const lastValue = useRef("")

    useEffect(() => {
        if (
            typeof window === "undefined" ||
            typeof document === "undefined" ||
            typeof MutationObserver === "undefined"
        )
            return
        const slotted = Array.isArray(collectionList)
            ? collectionList.some(Boolean)
            : Boolean(collectionList)
        const root =
            slotted && sourceRef.current
                ? sourceRef.current
                : document
        const read = () => {
            const seen = new Set<string>()
            const next = Array.from(
                root.querySelectorAll<HTMLElement>("[data-story-cms-item]")
            )
                .map((node) => {
                    const order = Number(node.dataset.order || 0)
                    return {
                        order,
                        story: {
                            image: {
                                src:
                                    node.dataset.thumbnail ||
                                    node.dataset.heroImage ||
                                    "",
                                alt:
                                    node.dataset.clientName ||
                                    node.dataset.cardTitle ||
                                    "",
                            },
                            alt: node.dataset.clientName || "",
                            lead:
                                node.dataset.cardTitle ||
                                node.dataset.title ||
                                "",
                            tail:
                                node.dataset.cardTitleMuted ||
                                node.dataset.subtitle ||
                                "",
                            href:
                                node.dataset.buttonLink ||
                                (node.dataset.slug
                                    ? `/work/${node.dataset.slug}`
                                    : "/work"),
                            cta: "SEE WORK",
                        } satisfies StoryItem,
                    }
                })
                .filter((entry) => {
                    const key = entry.story.lead || entry.story.href
                    if (!key || seen.has(key)) return false
                    seen.add(key)
                    return true
                })
                .sort((a, b) => a.order - b.order)
                .map((entry) => entry.story)
            const value = JSON.stringify(next)
            if (value !== lastValue.current) {
                lastValue.current = value
                setStories(next)
            }
        }
        read()
        const observer = new MutationObserver(read)
        observer.observe(root, {
            childList: true,
            subtree: true,
            attributes: true,
        })
        const timer = window.setTimeout(read, 300)
        return () => {
            observer.disconnect()
            window.clearTimeout(timer)
        }
    }, [collectionList])

    return { sourceRef, stories }
}

/**
 * IRG homepage work rail. Brightwell/Logline behavior, IRG type and tokens.
 *
 * @framerIntrinsicWidth 1280
 * @framerIntrinsicHeight 560
 * @framerSupportedLayoutWidth any-prefer-fixed
 * @framerSupportedLayoutHeight auto
 */
export default function IRGWorkCarousel(props: IRGWorkCarouselProps) {
    const {
        style,
        stories = STORIES,
        contentWidth = 1440,
        bleedRight = 32,
        mobileGap = 16,
        mobilePeek = 0,
        collectionList = props.cMSCollection,
    } = props
    const rootRef = useRef<HTMLDivElement>(null)
    const viewportRef = useRef<HTMLDivElement>(null)
    const cms = useCMSStories(collectionList)
    const drag = useRef<{
        id: number
        x: number
        sl: number
        moved: boolean
    } | null>(null)
    const suppressClick = useRef(false)
    const [atStart, setAtStart] = useState(true)
    const [atEnd, setAtEnd] = useState(false)
    const scrollTimer = useRef<number | undefined>(undefined)
    const revealLeft = () => {
        if (viewportRef.current) viewportRef.current.dataset.moved = "true"
    }

    const resolvedStories = useMemo(() => {
        const fromCms = cms.stories.filter((story) => story.lead)
        const source =
            fromCms.length > 0
                ? fromCms
                : stories.length > 0
                  ? stories
                  : STORIES
        return source.map((story, index) => {
            const fallback = STORIES[index % STORIES.length]
            return {
                ...fallback,
                ...story,
                cta: (story.cta || "SEE WORK").toUpperCase(),
                image: story.image?.src ? story.image : fallback.image,
            }
        })
    }, [cms.stories, stories])

    const N = resolvedStories.length

    const strideOf = useCallback((viewport: HTMLDivElement) => {
        const firstCard = viewport.querySelector(
            ".sc-card"
        ) as HTMLElement | null
        if (!firstCard) return 437
        const track = firstCard.parentElement
        const gap = track
            ? parseFloat(getComputedStyle(track).gap || "32") || 32
            : 32
        return firstCard.clientWidth + gap
    }, [])

    useEffect(() => () => window.clearTimeout(scrollTimer.current), [])

    const move = useCallback(
        (direction: number) => {
            const viewport = viewportRef.current
            if (!viewport) return
            revealLeft()
            const reduced =
                typeof window !== "undefined" &&
                window.matchMedia("(prefers-reduced-motion: reduce)").matches
            viewport.scrollBy({
                left: direction * strideOf(viewport),
                behavior: reduced ? "auto" : "smooth",
            })
        },
        [strideOf]
    )

    const onPointerDown = (event: ReactPointerEvent<HTMLDivElement>) => {
        if (event.pointerType !== "mouse") {
            revealLeft()
            return
        }
        if (event.button !== 0) return
        suppressClick.current = false
        const viewport = viewportRef.current
        if (!viewport) return
        drag.current = {
            id: event.pointerId,
            x: event.clientX,
            sl: viewport.scrollLeft,
            moved: false,
        }
    }
    const onPointerMove = (event: ReactPointerEvent<HTMLDivElement>) => {
        const d = drag.current
        const viewport = viewportRef.current
        if (!d || d.id !== event.pointerId || !viewport) return
        const dx = event.clientX - d.x
        if (!d.moved && Math.abs(dx) <= 8) return
        revealLeft()
        if (!d.moved) event.currentTarget.setPointerCapture(event.pointerId)
        d.moved = true
        viewport.style.scrollSnapType = "none"
        viewport.scrollLeft = d.sl - dx
    }
    const onPointerUp = (event: ReactPointerEvent<HTMLDivElement>) => {
        const d = drag.current
        if (!d || d.id !== event.pointerId) return
        drag.current = null
        suppressClick.current = d.moved
        if (event.currentTarget.hasPointerCapture(event.pointerId))
            event.currentTarget.releasePointerCapture(event.pointerId)
        if (viewportRef.current) viewportRef.current.style.scrollSnapType = ""
    }

    useEffect(() => {
        if (typeof window === "undefined") return
        const el = rootRef.current
        if (!el) return

        const update = () => {
            const bounds = el.getBoundingClientRect()
            const left = Math.max(0, bounds.left)
            const right = Math.max(
                0,
                document.documentElement.clientWidth - bounds.right
            )
            const inset =
                bounds.width <= 650
                    ? 0
                    : left
            el.style.setProperty("--sc-edge-left", left + "px")
            el.style.setProperty("--sc-edge-right", right + "px")
            el.style.setProperty("--sc-inset", inset + "px")
            const screenWidth = document.documentElement.clientWidth
            const phone = screenWidth < 810
            const tablet = screenWidth < 1200 && !phone
            const gap = phone ? mobileGap : tablet ? 24 : 32
            const visible = phone ? 1.1 : tablet ? 2.2 : 3.5
            const available = screenWidth - left
            el.style.setProperty("--sc-gap", `${gap}px`)
            el.style.setProperty("--sc-card-width", `${(available - Math.floor(visible) * gap) / visible}px`)
            const viewport = viewportRef.current
            if (viewport) {
                const max = Math.max(
                    0,
                    viewport.scrollWidth - viewport.clientWidth
                )
                setAtStart(viewport.scrollLeft <= 2)
                setAtEnd(viewport.scrollLeft >= max - 2)
            }
        }

        update()
        window.addEventListener("resize", update)
        const observer =
            typeof ResizeObserver === "undefined"
                ? null
                : new ResizeObserver(update)
        observer?.observe(el)
        const observedSection = el.closest("section")
        if (observedSection && observedSection !== el)
            observer?.observe(observedSection)
        return () => {
            window.removeEventListener("resize", update)
            observer?.disconnect()
        }
    }, [N, contentWidth, mobileGap, mobilePeek, strideOf])

    useEffect(() => {
        const viewport = viewportRef.current
        if (!viewport || N === 0 || typeof window === "undefined") return
        const start = () => {
            viewport.scrollLeft = 0
            const max = Math.max(0, viewport.scrollWidth - viewport.clientWidth)
            setAtStart(true)
            setAtEnd(max <= 2)
        }
        start()
        const raf = window.requestAnimationFrame(start)
        const observer = new ResizeObserver(start)
        observer.observe(viewport)
        return () => {
            window.cancelAnimationFrame(raf)
            observer.disconnect()
        }
    }, [N, strideOf])

    return (
        <div
            ref={rootRef}
            data-irg-work-carousel
            style={{
                ...style,
                position: "relative",
                width: "100%",
                ["--sc-content" as string]: `${contentWidth}px`,
                ["--sc-bleed-right" as string]: `${bleedRight}px`,
                ["--sc-mobile-gap" as string]: `${mobileGap}px`,
            }}
        >
            <div
                ref={cms.sourceRef}
                style={{ display: "none" }}
                aria-hidden="true"
            >
                {collectionList}
            </div>
            <style>{css}</style>
            <div className="sc-controls">
                <button
                    type="button"
                    className="sc-arrow"
                    onClick={() => move(-1)}
                    disabled={atStart}
                    aria-label="Previous work"
                >
                    ←
                </button>
                <button
                    type="button"
                    className="sc-arrow"
                    onClick={() => move(1)}
                    disabled={atEnd}
                    aria-label="Next work"
                >
                    →
                </button>
            </div>
            <div
                className="sc-viewport"
                ref={viewportRef}
                onScroll={() => {
                    const viewport = viewportRef.current
                    if (!viewport) return
                    const max = Math.max(
                        0,
                        viewport.scrollWidth - viewport.clientWidth
                    )
                    setAtStart(viewport.scrollLeft <= 2)
                    setAtEnd(viewport.scrollLeft >= max - 2)
                    window.clearTimeout(scrollTimer.current)
                }}
                onWheel={(event) => {
                    if (event.deltaX) revealLeft()
                }}
                tabIndex={0}
                role="region"
                aria-label="Selected work"
                onKeyDown={(event) => {
                    if (
                        event.target !== event.currentTarget ||
                        !["ArrowLeft", "ArrowRight"].includes(event.key)
                    )
                        return
                    event.preventDefault()
                    move(event.key === "ArrowLeft" ? -1 : 1)
                }}
                onClickCapture={(event) => {
                    if (!suppressClick.current || event.detail === 0) return
                    event.preventDefault()
                    event.stopPropagation()
                    suppressClick.current = false
                }}
                onPointerDown={onPointerDown}
                onPointerMove={onPointerMove}
                onPointerUp={onPointerUp}
                onPointerCancel={onPointerUp}
                onDragStart={(event) => event.preventDefault()}
            >
                <div className="sc-track">
                    {resolvedStories.map((story, index) => {
                        const src =
                            imageSrc(story.image) || story.image?.src || ""
                        return (
                            <article
                                className="sc-card"
                                key={`${story.lead}-${index}`}
                            >
                                <div
                                    className="sc-media"
                                    style={
                                        src
                                            ? {
                                                  backgroundImage: `url("${src}")`,
                                                  backgroundSize: "cover",
                                                  backgroundPosition: "center",
                                              }
                                            : undefined
                                    }
                                >
                                    {src ? (
                                        <img
                                            src={src}
                                            alt={
                                                story.alt ||
                                                story.image?.alt ||
                                                ""
                                            }
                                            srcSet={story.image?.srcSet}
                                            loading="lazy"
                                            decoding="async"
                                            draggable={false}
                                        />
                                    ) : (
                                        <div className="sc-ph">
                                            Format example
                                        </div>
                                    )}
                                </div>
                                <div className="sc-copy">
                                    <h3 className="sc-lead">{story.lead}</h3>
                                    <p className="sc-tail">{story.tail}</p>
                                    <a
                                        className="sc-link"
                                        href={hrefOf(story.href) || "/work"}
                                        aria-label={
                                            "See work: " + story.lead
                                        }
                                    >
                                        {story.cta || "SEE WORK"}{" "}
                                        <svg
                                            aria-hidden="true"
                                            width="16"
                                            height="16"
                                            viewBox="0 0 16 16"
                                            fill="none"
                                        >
                                            <path
                                                d="M3 8h10M9 4l4 4-4 4"
                                                stroke="currentColor"
                                                strokeWidth="1.6"
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                            />
                                        </svg>
                                    </a>
                                </div>
                            </article>
                        )
                    })}
                </div>
            </div>
        </div>
    )
}

addPropertyControls(IRGWorkCarousel, {
    contentWidth: {
        type: ControlType.Number,
        title: "Content width",
        defaultValue: 1440,
        min: 640,
        max: 1700,
        step: 10,
        unit: "px",
    },
    bleedRight: {
        type: ControlType.Number,
        title: "Bleed right",
        defaultValue: 32,
        min: 0,
        max: 80,
        step: 1,
        unit: "px",
    },
    mobileGap: {
        type: ControlType.Number,
        title: "Mobile gap",
        defaultValue: 16,
        min: 0,
        max: 64,
        step: 4,
        unit: "px",
    },
    mobilePeek: {
        type: ControlType.Number,
        title: "Mobile offset",
        defaultValue: 0,
        min: 0,
        max: 80,
        step: 4,
        unit: "px",
    },
    cMSCollection: { type: ControlType.Slot, title: "CMS Collection" },
    stories: {
        type: ControlType.Array,
        title: "Stories",
        control: {
            type: ControlType.Object,
            controls: {
                image: { type: ControlType.ResponsiveImage, title: "Image" },
                alt: { type: ControlType.String, title: "Alt" },
                lead: {
                    type: ControlType.String,
                    title: "Lead",
                    displayTextArea: true,
                },
                tail: {
                    type: ControlType.String,
                    title: "Tail",
                    displayTextArea: true,
                },
                href: { type: ControlType.Link, title: "Link" },
                cta: {
                    type: ControlType.String,
                    title: "CTA",
                    defaultValue: "SEE WORK",
                },
            },
        },
        defaultValue: STORIES,
    },
})
