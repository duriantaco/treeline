build-frontend:
	cd treeline-frontend && npm run build
	cp -r treeline-frontend/dist/* treeline/static/