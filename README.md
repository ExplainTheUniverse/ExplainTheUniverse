



## Technical Implementation and Operation Notes

### Project backup with datetime
cd ..
zip -r "$(date +"%Y-%m-%d_%H-%M-%S")_UnidadeCosmica.zip" UnidadeCosmica

### Markdowm fixes

* o1-preview 
search: \n([1-9]|[1-9][0-9])\. \*\*
replace: \n#### $1. **

* sonnet
search: \*\*: 
replace: **: \n