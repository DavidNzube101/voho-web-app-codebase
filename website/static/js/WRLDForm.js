function showStatusText(display_property, text, category){
	if (category == "error") {
		document.querySelector(".status-text").style.display = `${display_property}`
		document.querySelector(".status-text").innerHTML = `${text}`
		document.querySelector(".status-text").style.background = '#ff00002e'
		document.querySelector(".status-text").style.color = 'red'
	} if (category == "success") {
		document.querySelector(".status-text").style.display = `${display_property}`
		document.querySelector(".status-text").innerHTML = `${text}`
		document.querySelector(".status-text").style.background = '#00ff352e'
		document.querySelector(".status-text").style.color = 'green'
	} else {
		document.querySelector(".status-text").style.display = `${display_property}`
		document.querySelector(".status-text").innerHTML = `${text}`
		document.querySelector(".status-text").style.background = '#ffb2002e'
		document.querySelector(".status-text").style.color = 'orange'
	}
}
function hideStatusText(){
	document.querySelector(".status-text").style.display = 'none'
}

function submitForm (form_id, delay) {
	showLoader();
	setTimeout(()=>{
		try{
			if (document.querySelector("#faculty").value == "Select a Faculty" || document.querySelector("#department").value == "Select a Department") {
				hideLoader();
				setTimeout(()=>{
					hideStatusText()
				} , 4000)
				showStatusText('flex', 'Select Faculty or Department')
			} else {
				document.getElementById(form_id).submit()
			}
		} catch (e) {
			console.log(`Not in Onboarding.html\n${e}`);
		}
		try {
			setTimeout(()=>{
				document.getElementById(form_id).submit()

			} , 2000)
		} catch(e) {
			// statements
			console.log(`In Onboaring Stages but someting went wrong\n${e}`);
		}
	}, delay)
}
try {
	setTimeout(()=>{
		document.querySelector(".status-text").style.display = 'none'
	} , 10000)
} catch(e) {
	console.log(`Status Text not used in Form\n${e}`);
}