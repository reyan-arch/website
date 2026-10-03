import { addPropertyControls, ControlType } from "framer"
import type { CSSProperties } from "react"

interface IRGWorkCmsItemProps {
    title?: string
    lead?: string
    tail?: string
    slug?: string
    client?: string
    order?: number
    featured?: boolean
    image?: { src?: string; srcSet?: string; alt?: string }
    style?: CSSProperties
}

/**
 * Hidden CMS marker for IRGWorkCarousel. Bind Case Studies fields.
 *
 * @framerIntrinsicWidth 1
 * @framerIntrinsicHeight 1
 * @framerSupportedLayoutWidth fixed
 * @framerSupportedLayoutHeight fixed
 */
export default function IRGWorkCmsItem(props: IRGWorkCmsItemProps) {
    const {
        title = "",
        lead = "",
        tail = "",
        slug = "",
        client = "",
        order = 0,
        featured = false,
        image,
        style,
    } = props
    const src = image?.src || ""
    const href = slug ? `/work/${slug}` : "/work"

    return (
        <div
            data-story-cms-item=""
            data-title={title}
            data-card-title={lead || title}
            data-card-title-muted={tail}
            data-subtitle={tail}
            data-client-name={client}
            data-slug={slug}
            data-hero-image={src}
            data-thumbnail={src}
            data-button-link={href}
            data-order={String(order)}
            data-featured={featured ? "true" : "false"}
            style={{
                ...style,
                width: 1,
                height: 1,
                overflow: "hidden",
                position: "relative",
            }}
        />
    )
}

addPropertyControls(IRGWorkCmsItem, {
    title: { type: ControlType.String, title: "Title", defaultValue: "" },
    lead: { type: ControlType.String, title: "Lead", defaultValue: "" },
    tail: {
        type: ControlType.String,
        title: "Tail",
        defaultValue: "",
        displayTextArea: true,
    },
    slug: { type: ControlType.String, title: "Slug", defaultValue: "" },
    client: { type: ControlType.String, title: "Client", defaultValue: "" },
    order: {
        type: ControlType.Number,
        title: "Order",
        defaultValue: 0,
        displayStepper: true,
    },
    featured: {
        type: ControlType.Boolean,
        title: "Featured",
        defaultValue: false,
    },
    image: { type: ControlType.ResponsiveImage, title: "Image" },
})
