import * as React from "react"
import { addPropertyControls, ControlType } from "framer"

interface ResponsiveImage {
    src: string
    srcSet?: string
    alt?: string
}

interface GalleryItem {
    image: ResponsiveImage
}

interface IRGGalleryMosaicProps {
    images?: GalleryItem[]
    gap?: number
    radius?: number
    style?: React.CSSProperties
}

const fallbackImage: ResponsiveImage = {
    src: "https://framerusercontent.com/images/Pa3j0CpeCPC051WWeBVZWEFcQ.png",
    alt: "Campaign team reviewing creative work",
}

function placement(index: number, count: number): React.CSSProperties {
    if (count === 1) return { gridColumn: "1 / -1", gridRow: "1 / -1" }
    if (count === 2) return { gridColumn: index === 0 ? "1 / 8" : "8 / -1", gridRow: "1 / -1" }
    if (count === 3) return index === 0
        ? { gridColumn: "1 / 8", gridRow: "1 / -1" }
        : { gridColumn: "8 / -1", gridRow: index === 1 ? "1 / 2" : "2 / 3" }
    const columnStart = index % 2 === 0 ? 1 : 7
    const rowStart = Math.floor(index / 2) + 1
    return { gridColumn: columnStart + " / span 6", gridRow: rowStart + " / span 1" }
}

/**
 * @framerSupportedLayoutWidth any-prefer-fixed
 * @framerSupportedLayoutHeight any-prefer-fixed
 */
export default function IRGGalleryMosaic(props: IRGGalleryMosaicProps) {
    const { images = [{ image: fallbackImage }], gap = 12, radius = 24, style } = props
    const visibleImages = images.map((item) => item?.image).filter((image): image is ResponsiveImage => Boolean(image?.src)).slice(0, 6)
    const rows = visibleImages.length <= 3 ? 2 : Math.ceil(visibleImages.length / 2)

    return (
        <section
            aria-label="Case study gallery"
            style={{
                ...style,
                position: "relative",
                display: visibleImages.length ? "grid" : "none",
                gridTemplateColumns: "repeat(12, minmax(0, 1fr))",
                gridTemplateRows: "repeat(" + rows + ", minmax(0, 1fr))",
                gap,
                width: "100%",
                height: "100%",
                overflow: "hidden",
            }}
        >
            {visibleImages.map((image, index) => (
                <img
                    key={image.src + index}
                    src={image.src}
                    srcSet={image.srcSet}
                    alt={image.alt || ""}
                    style={{
                        ...placement(index, visibleImages.length),
                        width: "100%",
                        height: "100%",
                        objectFit: "cover",
                        borderRadius: radius,
                        minHeight: 0,
                    }}
                />
            ))}
        </section>
    )
}

addPropertyControls(IRGGalleryMosaic, {
    images: {
        type: ControlType.Array,
        title: "Images",
        control: {
            type: ControlType.Object,
            controls: {
                image: { type: ControlType.ResponsiveImage, title: "Image" },
            },
        },
        defaultValue: [{ image: fallbackImage }],
        maxCount: 12,
    },
    gap: {
        type: ControlType.Number,
        title: "Gap",
        defaultValue: 12,
        min: 0,
        max: 32,
        step: 1,
    },
    radius: {
        type: ControlType.Number,
        title: "Radius",
        defaultValue: 24,
        min: 0,
        max: 48,
        step: 1,
    },
})
