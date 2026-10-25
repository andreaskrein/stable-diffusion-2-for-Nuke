![Nuke](https://img.shields.io/badge/Nuke-17.1v2-F5B335?style=flat&logo=nuke&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11.11-3776AB?style=flat&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.7.1-EE4C2C?style=flat&logo=pytorch&logoColor=white)

# Stable Diffusion inpainting for Nuke
## Runs Stable Diffusion 2 in an Inference node

### Installation
1. Place the content of this repo into a folder in your local Cattery directory,   
   for example `~/.nuke/Cattery/stable-diffusion-2-for-Nuke`

3. Models not included. Get them [here](https://huggingface.co/andreaskrein/stable-diffusion-2-inpainting/resolve/main/stable-diffusion-2-inpainting.cat) and [here](https://huggingface.co/andreaskrein/open-clip-vit-h/resolve/main/open-clip-vit-h.cat), then put them inside this folder as well

5. in Nuke, update the Cattery (**Cattery > Update**)
   
   ![Cattery menu](https://raw.githubusercontent.com/andreaskrein/andreaskrein.github.io/master/assets/Cattery.png)
 

  
> [!NOTE]
> In the current experimental implementation, copied Gizmos lose their encoded text tokens.   
> If this happens, simply press the Encode button again to re-encode them.
