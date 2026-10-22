"""Writes the channel's catalog (signature and description of each registered piece).

Use from the channel (e.g. channel/catalog.py):  from reels_engine.catalog import generate; generate()
What gets documented comes from the channel configuration: catalog_header, catalog_api, catalog_maps and catalog_out."""
import ast, importlib, importlib.util, os
from .config import current

def sig(fn, name=None):
    a = fn.args; names = [x.arg for x in a.args]; dfl = [None] * (len(names) - len(a.defaults)) + [ast.unparse(x) for x in a.defaults]
    ps = [n if v is None else f"{n}={v}" for n, v in zip(names, dfl)]
    if a.vararg: ps.append("*" + a.vararg.arg)
    ps += [k.arg for k in a.kwonlyargs]
    if a.kwarg: ps.append("**" + a.kwarg.arg)
    return f"{name or fn.name}({', '.join(ps)})"

def path_of(mod, paths=None):
    """A module's .py file, without running it."""
    for pre, folder in (paths or {}).items():
        if mod == pre or mod.startswith(pre + "."):
            return os.path.join(folder, *mod[len(pre):].lstrip(".").split(".")) + ".py" if mod != pre else os.path.join(folder, "__init__.py")
    spec = importlib.util.find_spec(mod)
    return spec.origin

def generate(cfg=None, out_path=None):
    cfg = cfg or current()
    paths = {k: (v if os.path.isabs(v) else os.path.join(cfg.root, v)) for k, v in cfg.catalog_paths.items()}
    out = list(cfg.catalog_header)
    for title, mod in cfg.catalog_api:
        out.append(f"\n## {title}\n")
        for n in ast.walk(ast.parse(open(path_of(mod, paths)).read())):
            if isinstance(n, ast.FunctionDef) and not n.name.startswith("_"):
                doc = (ast.get_docstring(n) or "").split("\n")[0]
                out.append(f"- `{sig(n)}`" + (f" — {doc}" if doc else ""))
    for f in cfg.catalog_maps:
        M = importlib.import_module(f); out.append(f"\n## {f}\n")
        for k, v in sorted(M.MAP.items()):
            mod, _, real = v.partition(":")
            node = next((n for n in ast.parse(open(path_of(mod, paths)).read()).body if isinstance(n, ast.FunctionDef) and n.name == (real or k)), None)
            doc = (ast.get_docstring(node) or "").split("\n")[0] if node else ""
            out.append(f"- `{sig(node, k) if node else k}` · {mod}" + (f" — {doc}" if doc else ""))
    p = out_path or os.path.join(cfg.root, cfg.catalog_out)
    open(p, "w").write("\n".join(out) + "\n")
    print(len(out), "lines →", p)
    return p

if __name__ == "__main__":
    generate()
