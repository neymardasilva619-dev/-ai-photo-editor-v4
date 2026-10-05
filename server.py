import os, base64, tempfile
from flask import Flask, request, jsonify, send_from_directory
from openai import OpenAI

app = Flask(__name__, static_folder='.')

@app.get('/')
def index():
    return send_from_directory('.', 'index.html')

@app.get('/api/health')
def health():
    return jsonify(ok=True, configured=bool(os.environ.get('OPENAI_API_KEY')))
def data_url_to_bytes(s):
    if not s:
        raise ValueError('Invalid image data')

    if not isinstance(s, str):
        raise ValueError('Invalid image data')

    s = s.strip()

    # Обычный Data URL:
    # data:image/png;base64,AAAA...
    if s.startswith('data:'):
        if ',' not in s:
            raise ValueError('Invalid image data')
        head, body = s.split(',', 1)

        if ';base64' not in head.lower():
            raise ValueError('Image must be base64 data')
    else:
        # Также принимаем обычный Base64 без data:image/... префикса
        body = s

    body = ''.join(body.split())

    if not body:
        raise ValueError('Invalid image data')

    try:
        return base64.b64decode(body, validate=True)
    except Exception:
        try:
            body += '=' * (-len(body) % 4)
            return base64.b64decode(body)
        except Exception:
            raise ValueError('Invalid image data')
@app.post('/api/edit')
def edit():
    data = request.get_json(force=True)
    prompt = (data.get('prompt') or '').strip()
    image = data.get('image') or ''
    mask = data.get('mask') or ''
    if not prompt or not image:
        return jsonify(error='prompt/image required'), 400
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return jsonify(error='OPENAI_API_KEY is not configured on the server.'), 503
    try:
        client = OpenAI(api_key=api_key)
        img_bytes = data_url_to_bytes(image)
        img_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img_file.write(img_bytes); img_file.close()
        files = [open(img_file.name, 'rb')]
        # The Images API supports image edits with a prompt and optional mask.
        kwargs = {'model': 'gpt-image-1', 'image': files, 'prompt': prompt, 'size': 'auto'}
        mask_path = None
        if mask and mask.startswith('data:image/'):
            mask_bytes = data_url_to_bytes(mask)
            mask_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            mask_file.write(mask_bytes); mask_file.close()
            mask_path = mask_file.name
            kwargs['mask'] = open(mask_path, 'rb')
        result = client.images.edit(**kwargs)
        b64 = result.data[0].b64_json
        return jsonify(image='data:image/png;base64,' + b64)
    except Exception as e:
        return jsonify(error=str(e)), 500
    finally:
        for f in locals().get('files', []):
            try: f.close()
            except: pass
        for p in [locals().get('img_file').name if locals().get('img_file') else None, locals().get('mask_path')]:
            if p:
                try: os.unlink(p)
                except: pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '8787')), debug=False)
