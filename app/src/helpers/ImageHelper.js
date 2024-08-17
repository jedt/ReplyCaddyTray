function getHighResImage(url) {
    const pixelRatio = window.devicePixelRatio || 1;
    if (pixelRatio > 1) {
        return url.replace('.png', '@2x.png');
    }
    return url;
}

export function Image(props) {
    const imgUrl = getHighResImage(props.src);
    // preserve the original ratio

    return <img width={props.width} height={props.height} src={imgUrl} alt="Sample" />;
}
