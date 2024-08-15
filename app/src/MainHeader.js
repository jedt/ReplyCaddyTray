
function onClick() {
  console.log("Button clicked");
}
export default function MainHeader() {
  return (
    <div className={"thumbnailContainer"}>
      <button className={"thumbnailWrapper"} onClick={onClick}>
        <div className={"imageIcon"}>
          <img className={"pdf"} src={"./images/pdf-thumbnail-icon.png"} alt={"pdf"} />
        </div>
        <div className={"textTitle"}>
          <span>PDF Files</span>
        </div>
        <div className={"textTotal"}>
          <span>10 Files</span>
        </div>
      </button>
      <button className={"thumbnailWrapper"} onClick={onClick}>
        <div className={"imageIcon"}>
          <img className={"pdf"} src={"./images/google-sheets-icon.png"} alt={"pdf"} />
        </div>
        <div className={"textTitle"}>
          <span>Google Sheets</span>
        </div>
        <div className={"textTotal"}>
          <span>71 Files</span>
        </div>
      </button>
    </div>
  );
}
