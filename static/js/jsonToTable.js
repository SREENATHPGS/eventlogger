let convertJsonToTable = (tableParentId, data, selectableRows = false, selectedCallback = undefined) => {
	
	console.log("Converting json to table:");
	// console.log(data);
	// Extract value from table header. 
	let col = [];
	col.push("Index");
	for (let i = 0; i < data.length; i++) {
		for (let key in data[i]) {
			if (col.indexOf(key) === -1) {
				col.push(key);
			}
		}
	}

	//Adding select radio button if needed.
	if (selectableRows) {
		col.push("Select");
	}
	
	// Create table.
	const table = document.createElement("table");
	
	// Create table header row using the extracted headers above.
	let tr = table.insertRow(-1);                   // table row.
	
	for (let i = 0; i < col.length; i++) {
		let th = document.createElement("th");      // table header.
		th.innerHTML = col[i];
		tr.appendChild(th);
	}
	
	// add json data to the table as rows.
	for (let i = 0; i < data.length; i++) {
		
		tr = table.insertRow(-1);
		
		for (let j = 0; j < col.length; j++) {
			let tabCell = tr.insertCell(-1);
			let txt = data[i][col[j]];

			//Adding index
			if (j == 0) {
				txt = i+1;
				tabCell.innerHTML = txt;
				continue;
			}

			//Conveting JSON to text
			if (typeof(txt) == "object") {
				txt = JSON.stringify(txt);
			}

			//Adding Select Radio Element
			if (selectableRows && j == col.length - 1) {
				let checkbox = document.createElement("input");
				checkbox.type = "checkbox";
				checkbox.index = i;
				checkbox.addEventListener("click", selectedCallback);
				tabCell.appendChild(checkbox);
			} else {
				tabCell.innerHTML = txt;
			}
		}
	}
	
	// Now, add the newly created table with json data, to a container.
	const divShowData = document.getElementById(tableParentId);
	divShowData.innerHTML = "";
	divShowData.appendChild(table);
}