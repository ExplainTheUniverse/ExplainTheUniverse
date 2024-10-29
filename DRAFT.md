
### Technical Memo Notes

#### Project backup with datetime
cd ..
zip -r "$(date +"%Y-%m-%d_%H-%M-%S")_UnidadeCosmica.zip" UnidadeCosmica

#### Result markdowm fixes

* o1-preview 
search: \n([1-9]|[1-9][0-9])\. \*\*
replace: \n#### $1. **

* sonnet
search: \*\*: 
replace: **: \n

* Command R+
search: :\*\*\n- 
replace: :**\n\n- 


