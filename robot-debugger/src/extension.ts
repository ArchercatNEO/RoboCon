import * as fs from 'fs/promises';
import JSZip from "jszip";
import * as vscode from 'vscode';

interface File {
	name: string,
	path: string,
	content: string
}

async function* recursiveRead(dirPath: string): AsyncGenerator<File> {
	const files = await fs.opendir(dirPath);
	for await (const file of files) {
		const path = dirPath + '/' + file.name;
		if (file.isFile()) {
			const content = await fs.readFile(path, {
				encoding: "utf-8",
			});
			yield { name: file.name, path, content};

		} else if (file.isDirectory()) {
			for await (const file of recursiveRead(path)) {
				yield file;
			}
		}
	}
}

export function activate(context: vscode.ExtensionContext) {
	let window: vscode.WebviewPanel; 

	//files
	//files/delete
	const sync = vscode.commands.registerCommand("brainbox.sync", async () => {
		for await (const file of recursiveRead("./Dev/RoboCon/2023-2024")) {
			await fetch(`http://192.168.4.1/files/save/${file.name}`, {
				method: "POST",
				body: file.content
			});
			console.log(`Saved file ${file.path}`);
		}
	});
	context.subscriptions.push(sync);

	const start = vscode.commands.registerCommand("brainbox.start", async () => {
		if (window) {
			console.log("Robot is already active, stop it first");
			return;
		}
		
		window = vscode.window.createWebviewPanel("web", "Robocon logs", vscode.ViewColumn.Beside, {
			enableScripts: true
		});
		window.webview.html = "<!DOCTYPE html>";
		
		window.webview.html += "<p> Packing files into zip.. </p>";
		const zip = new JSZip();
		for await (const file of recursiveRead("./Dev/RoboCon/2023-2024")) {
			zip.file(file.name, file.content);
		}
		
		const uploadBody = new FormData();
		const blob = await zip.generateAsync({
			type: "blob"
		});
		uploadBody.append("uploaded_file", blob, "code.zip");
		
		window.webview.html += "<p> Waiting for brainbox to unpack zip.. </p>";
		await fetch("http://192.168.4.1/upload/upload", {
			method: "POST",
			body: uploadBody
		});
		
		const startBody = new FormData();
		startBody.append("zone", "0");
		startBody.append("mode", "development");
		
		window.webview.html += "<p> Starting robot </p>";
		await fetch("http://192.168.4.1/run/start", {
			method: "POST",
			body: startBody
		});
		
		window.webview.html = `
		<!DOCTYPE html>
		<html>
			<head>
				<script type="module">
				const logText = document.getElementById("logs");
				const img = document.getElementById("image");
				setInterval(async () => {
					const res = await fetch("http://192.168.4.1/run/output");
					const text = await res.text();
					logText.innerText = text
					img.src = "http://192.168.4.1/static/image.jpg";
				}, 1000)
				</script>
			</head>
			<body>
				<img id=image src="http://192.168.4.1/static/image.jpg" width="800" height="600" alt="Robot camera data">
				<pre id="logs" style="overflow-y:scroll; height:400px;"></pre>
			</body>
		</html>
		`;
	});
	context.subscriptions.push(start);
	
	const stop = vscode.commands.registerCommand("brainbox.stop", () => {
		window.dispose();

		fetch("http://192.168.4.1/run/stop", { method: "POST"});
	});
	context.subscriptions.push(stop);
}

export function deactivate() {}
