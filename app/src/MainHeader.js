import {Image} from "./helpers/ImageHelper";

function onClick() {
  console.log("Button clicked");
}
export default function MainHeader() {
  return (
    <div className={"tabContainer"}>
      <div className={"tabItem"}>
        <div className={"selected"}>Pdf Files</div>
      </div>
      <div className={"tabItem"}>
        <div>Word Documents</div>
      </div>
    </div>
  );
}
