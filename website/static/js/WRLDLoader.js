let container_loader = document.querySelector(".container-loader")
let container_content = document.querySelector(".container-content")
let loader_asset = document.querySelector(".loader-asset")

function showLoader(){
	loader_asset.style.display = 'flex'
	container_content.style.opacity = "0.4"
}
function hideLoader(){
	loader_asset.style.display = 'none'
	container_content.style.opacity = "1"
}
hideLoader()