# Lim Lab - Website #

**Website of the Lim Lab at UCSF.**

[Check out the live site.](https://limlab.ucsf.edu)

Contact Hersh Bhargava with questions.

Internal notes: https://www.notion.so/hershbhargava/Lim-Lab-Website-Reference-b64071ae9952440f9922b39ea1ac9c2b?pvs=4

The repository will contain `develop` and `master` branches. 

# Architecture

This site was developed using `jade` and `sass` for templating and styling, respectively. The site is built using `grunt`, which is built on `node.js`.

See below for environment setup instructions. The source code is in the `src` directory, and the built site is in the `dest` directory.

`Gruntfile.js` tells Grunt how to build the site. `package.json` contains the Node dependencies for the build process.

# Contributing

To contribute changes, submit a pull request. Ensure that the Github Actions build test passes.

# Environment Config and Usage

Use the script `./config_conda_env.sh` to build the `limlab-website` conda environment.

Then, to build the site, in the root directory, call:

```bash
conda activate limlab-website
grunt
```